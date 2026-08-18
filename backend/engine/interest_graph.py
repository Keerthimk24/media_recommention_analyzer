"""
backend/engine/interest_graph.py

Manages the latent, evolving user interest graph, engagement-weighted signal updates,
hierarchical leaf-to-parent propagation, temporal exponential decay, curiosity vs. commitment
trajectory tracking, and the interactive feedback loop.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime, timedelta
import math
import json
from .taxonomy import TaxonomyGraph, DOMAIN_ROLLUPS

# Engagement Signal Weights (Part A.5)
ENGAGEMENT_WEIGHTS = {
    "skip": -0.80,              # Skip < 2s: Strong negative
    "watch_50": 0.20,           # Watch 50%: Weak positive
    "watch_90": 0.60,           # Watch 90%+: Positive
    "replay": 0.80,             # Replay: Strong positive
    "like": 0.50,               # Like: Positive
    "save": 0.90,               # Save: Very strong positive
    "share": 0.90,              # Share: Very strong positive
    "follow_creator": 1.00      # Follow: Extremely strong positive
}

# Exponential decay half-life in days for interest evolution
DECAY_HALF_LIFE_DAYS = 14.0


class UserInterestGraph:
    """
    Represents an evolving, engagement-weighted latent interest graph for a single user.
    """

    def __init__(self, user_id: str, primary_lang: str = "English", taxonomy: Optional[TaxonomyGraph] = None):
        self.user_id = user_id
        self.primary_lang = primary_lang
        self.taxonomy = taxonomy or TaxonomyGraph()
        
        # Node weights: entity -> score (-1.0 to +1.0)
        self.entity_scores: Dict[str, float] = {}
        # Domain aggregate scores: domain -> score
        self.domain_scores: Dict[str, float] = {}
        # Interaction counts & temporal tracking
        self.interaction_count = 0
        self.history: List[Dict] = []
        # Trajectory tracking per topic: list of (timestamp, score_delta)
        self.topic_trajectories: Dict[str, List[Tuple[str, float]]] = {}
        # Language preference weights: language -> score (0.0 to 1.0)
        self.language_weights: Dict[str, float] = {primary_lang: 0.8, "English": 0.5}
        # Explicit topic blocks / negative penalties
        self.blocked_topics: Set[str] = set()
        self.boosted_topics: Set[str] = set()

    def process_interaction(self, interaction: Dict, reel_analysis: Dict):
        """
        Ingests a user interaction on a reel and updates the latent interest graph.
        """
        self.interaction_count += 1
        ts_str = interaction.get("timestamp", datetime.now().isoformat())
        
        # 1. Compute net engagement signal delta
        watch_pct = float(interaction.get("watch_percentage", 0))
        liked = int(interaction.get("liked", 0))
        saved = int(interaction.get("saved", 0))
        shared = int(interaction.get("shared", 0))
        replayed = int(interaction.get("replayed", 0))
        skipped = int(interaction.get("skipped", 0))
        followed = int(interaction.get("followed_creator", 0))
        
        delta = 0.0
        
        # Watch time contribution
        if skipped or watch_pct < 20:
            delta += ENGAGEMENT_WEIGHTS["skip"]
        elif watch_pct >= 90:
            delta += ENGAGEMENT_WEIGHTS["watch_90"]
        elif watch_pct >= 45:
            delta += ENGAGEMENT_WEIGHTS["watch_50"]
        else:
            delta += 0.05

        # Explicit action contributions
        if liked:
            delta += ENGAGEMENT_WEIGHTS["like"]
        if saved:
            delta += ENGAGEMENT_WEIGHTS["save"]
        if shared:
            delta += ENGAGEMENT_WEIGHTS["share"]
        if replayed:
            delta += ENGAGEMENT_WEIGHTS["replay"]
        if followed:
            delta += ENGAGEMENT_WEIGHTS["follow_creator"]

        # Hype penalty: if user watched hype, downweight unless saved/shared
        intent = reel_analysis.get("intent", "")
        if intent == "Hype" and delta > 0:
            delta *= 0.2  # severely discount accidental hype watch
        if intent == "Hype" and (skipped or watch_pct < 30):
            # Reward skipping hype: learn negative preference against hype
            self.entity_scores["Hype"] = max(-1.0, self.entity_scores.get("Hype", 0.0) - 0.5)

        # 2. Extract entities involved
        techs = reel_analysis.get("tech_entities", {})
        all_entities = (
            techs.get("programming_languages", []) +
            techs.get("frameworks", []) +
            techs.get("technologies", []) +
            techs.get("concepts", []) +
            techs.get("domains", [])
        )

        # If entertainment only, track as entertainment signal without polluting core tech domains
        if reel_analysis.get("intent") in ("Entertainment", "Meme") and not all_entities:
            self.entity_scores["Entertainment"] = max(-1.0, min(1.0, self.entity_scores.get("Entertainment", 0.0) + delta * 0.5))

        # 3. Update leaf entity nodes
        for entity in all_entities:
            old_score = self.entity_scores.get(entity, 0.0)
            # Soft bounding update
            new_score = max(-1.0, min(1.0, old_score + delta * 0.25))
            self.entity_scores[entity] = round(new_score, 4)

            # Record trajectory
            self.topic_trajectories.setdefault(entity, []).append((ts_str, delta))

            # 4. Propagate up to parent domain (Hierarchical Rollup)
            parent_domain = self.taxonomy.get_parent_domain(entity)
            if parent_domain:
                dom_old = self.domain_scores.get(parent_domain, 0.0)
                dom_new = max(-1.0, min(1.0, dom_old + delta * 0.20))
                self.domain_scores[parent_domain] = round(dom_new, 4)
                self.topic_trajectories.setdefault(parent_domain, []).append((ts_str, delta * 0.8))

        # 5. Track human language preference
        content_lang = reel_analysis.get("human_language", {}).get("base_language", "English")
        if delta > 0 and content_lang:
            self.language_weights[content_lang] = round(min(1.0, self.language_weights.get(content_lang, 0.3) + 0.05), 3)

        # Save history item
        self.history.append({
            "interaction_id": interaction.get("interaction_id"),
            "reel_id": reel_analysis.get("reel_id"),
            "timestamp": ts_str,
            "title": reel_analysis.get("raw_content", {}).get("title"),
            "category": reel_analysis.get("category_enum"),
            "delta": round(delta, 3),
            "watch_pct": watch_pct,
            "liked": bool(liked),
            "saved": bool(saved),
            "replayed": bool(replayed),
            "skipped": bool(skipped)
        })

    def apply_time_decay(self, reference_time: Optional[datetime] = None):
        """
        Applies exponential time decay to older interactions to prioritize evolving interests.
        Formula: weight = exp(-ln(2) * days_elapsed / half_life)
        """
        if not self.history:
            return

        ref_time = reference_time or datetime.now()
        decay_factor = math.log(2) / DECAY_HALF_LIFE_DAYS

        # Recalculate domain scores from decayed entity scores
        for entity in list(self.entity_scores.keys()):
            # check recency
            trajectories = self.topic_trajectories.get(entity, [])
            if trajectories:
                latest_ts_str, _ = trajectories[-1]
                try:
                    latest_ts = datetime.fromisoformat(latest_ts_str.replace("Z", ""))
                    days_elapsed = max(0.0, (ref_time - latest_ts).total_seconds() / 86400.0)
                    weight = math.exp(-decay_factor * (days_elapsed / 7.0))
                    self.entity_scores[entity] = round(self.entity_scores[entity] * weight, 4)
                except Exception:
                    pass

    def detect_trajectory_trend(self, topic: str) -> str:
        """
        Detects whether a user's interest in a topic is 'rising', 'stable', 'fading', or 'curiosity_declined'.
        """
        events = self.topic_trajectories.get(topic, [])
        if len(events) < 2:
            return "emerging"

        deltas = [d for _, d in events]
        recent_deltas = deltas[-3:]
        
        # Check for curiosity pattern: initial high followed by rapid decay/skips
        if len(deltas) >= 3 and deltas[0] > 0.5 and deltas[-1] < -0.3:
            return "curiosity_declined"

        avg_recent = sum(recent_deltas) / len(recent_deltas)
        avg_all = sum(deltas) / len(deltas)

        if avg_recent > avg_all + 0.15:
            return "rising"
        elif avg_recent < avg_all - 0.20:
            return "fading"
        else:
            return "stable"

    def apply_feedback(self, feedback_type: str, topic_or_category: str, detail: Optional[str] = None):
        """
        Interactive feedback loop (Part A.8):
        - 'useful' (👍): Reinforces recommended topic node (+0.35)
        - 'not_useful' (👎): Weakens recommended node (-0.35)
        - 'more_like_this' (🔥): Strongly boosts topic & related nodes (+0.60)
        - 'dont_show_topic' (🚫): Adds to blocked topics & sets weight to -1.0
        - 'prefer_language' (🌐): Adjusts human language preference bonus
        """
        if feedback_type == "useful":
            self.domain_scores[topic_or_category] = min(1.0, self.domain_scores.get(topic_or_category, 0.3) + 0.35)
            self.entity_scores[topic_or_category] = min(1.0, self.entity_scores.get(topic_or_category, 0.3) + 0.35)
            self.boosted_topics.add(topic_or_category)

        elif feedback_type == "not_useful":
            self.domain_scores[topic_or_category] = max(-1.0, self.domain_scores.get(topic_or_category, 0.0) - 0.35)
            self.entity_scores[topic_or_category] = max(-1.0, self.entity_scores.get(topic_or_category, 0.0) - 0.35)

        elif feedback_type == "more_like_this":
            self.domain_scores[topic_or_category] = min(1.0, self.domain_scores.get(topic_or_category, 0.4) + 0.60)
            self.entity_scores[topic_or_category] = min(1.0, self.entity_scores.get(topic_or_category, 0.4) + 0.60)
            self.boosted_topics.add(topic_or_category)

        elif feedback_type == "dont_show_topic":
            self.blocked_topics.add(topic_or_category)
            self.domain_scores[topic_or_category] = -1.0
            self.entity_scores[topic_or_category] = -1.0

        elif feedback_type == "prefer_language" and detail:
            self.language_weights[detail] = 0.95

    def get_top_inferred_interests(self, k: int = 3) -> List[Tuple[str, float, str]]:
        """
        Returns top k latent interests with their scores and trend.
        """
        # Combine domain scores and strong entity scores
        all_candidates = {}
        for dom, score in self.domain_scores.items():
            if dom not in self.blocked_topics:
                all_candidates[dom] = score

        for ent, score in self.entity_scores.items():
            if ent not in self.blocked_topics and ent not in all_candidates and score > 0.3:
                all_candidates[ent] = score * 0.9

        sorted_interests = sorted(all_candidates.items(), key=lambda kv: kv[1], reverse=True)
        results = []
        for name, score in sorted_interests[:k]:
            trend = self.detect_trajectory_trend(name)
            results.append((name, round(score, 3), trend))
        return results

    def get_confidence_level(self) -> str:
        """
        Confidence Rule (Part C):
        Low (< 5 interactions)
        Medium (5-15 interactions)
        High (> 15 interactions with consistent signal)
        """
        n = self.interaction_count
        if n < 5:
            return "Low"
        elif n < 15:
            return "Medium"
        else:
            # Check consistency
            top_interests = self.get_top_inferred_interests(1)
            if top_interests and top_interests[0][1] >= 0.45:
                return "High"
            return "Medium"

    def to_graph_data(self) -> Dict[str, Any]:
        """
        Exports the graph structure for interactive visualization in the frontend.
        """
        nodes = []
        links = []
        node_ids = set()

        # Add User Node
        nodes.append({
            "id": "USER",
            "label": f"Student ({self.user_id})",
            "type": "user",
            "size": 26,
            "color": "#38bdf8"
        })
        node_ids.add("USER")

        # Add Domain Nodes
        for dom, score in self.domain_scores.items():
            if score > -0.2 and dom not in self.blocked_topics:
                dom_id = f"DOM_{dom}"
                nodes.append({
                    "id": dom_id,
                    "label": dom,
                    "type": "domain",
                    "score": round(score, 2),
                    "trend": self.detect_trajectory_trend(dom),
                    "size": max(14, min(30, int(16 + score * 14))),
                    "color": "#a855f7" if score > 0.4 else "#64748b"
                })
                node_ids.add(dom_id)
                links.append({
                    "source": "USER",
                    "target": dom_id,
                    "weight": round(max(0.1, score), 2),
                    "type": "interest"
                })

        # Add Leaf Entity Nodes
        for ent, score in self.entity_scores.items():
            if score > 0.1 and ent not in self.blocked_topics and ent not in ["Entertainment", "Hype"]:
                ent_id = f"ENT_{ent}"
                nodes.append({
                    "id": ent_id,
                    "label": ent,
                    "type": "entity",
                    "score": round(score, 2),
                    "trend": self.detect_trajectory_trend(ent),
                    "size": max(10, min(22, int(12 + score * 10))),
                    "color": "#10b981" if score > 0.5 else "#3b82f6"
                })
                node_ids.add(ent_id)

                parent_dom = self.taxonomy.get_parent_domain(ent)
                dom_id = f"DOM_{parent_dom}"
                if dom_id in node_ids:
                    links.append({
                        "source": ent_id,
                        "target": dom_id,
                        "weight": round(max(0.1, score), 2),
                        "type": "rollup"
                    })
                else:
                    links.append({
                        "source": "USER",
                        "target": ent_id,
                        "weight": round(max(0.1, score), 2),
                        "type": "direct"
                    })

        return {
            "nodes": nodes,
            "links": links,
            "interaction_count": self.interaction_count,
            "confidence": self.get_confidence_level(),
            "top_interests": self.get_top_inferred_interests(3)
        }
