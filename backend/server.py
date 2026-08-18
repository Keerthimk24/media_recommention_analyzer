"""
backend/server.py

FastAPI Application for the AI Reels Interest-Inference & Tech Recommendation Agent.
Exposes RESTful endpoints for:
- User management and switching
- Interactive Reel feed and video playback simulation
- Live engagement recording (Watch %, Like, Save, Share, Replay, Skip, Follow)
- Real-time Interest Graph visualization and updates
- Live recommendations with exact Part A.9 explainable schema
- Feedback loop (👍 Useful, 👎 Not useful, 🔥 More like this, 🚫 Block topic, 🌐 Prefer language)
- 1-Click Trap & Benchmark Evaluation Lab
- Supabase cloud configuration and status
"""

import os
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

from .data_loader import DataLoader
from .engine.taxonomy import TaxonomyGraph, VALID_CATEGORIES, LEARNING_JOURNEY_STAGES
from .engine.multimodal_analyzer import MultimodalAnalyzer
from .engine.interest_graph import UserInterestGraph
from .engine.recommender import RecommenderEngine
from .engine.evaluator import BenchmarkEvaluator
from .engine.supabase_client import SupabaseClientAdapter

app = FastAPI(
    title="AI Reels Interest-Inference & Tech Recommendation Agent API",
    description="Multimodal interest-inference and progression-based technology recommender",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
data_loader = DataLoader(DATA_DIR)
taxonomy = TaxonomyGraph(os.path.join(DATA_DIR, "technology_relationships.csv"))
analyzer = MultimodalAnalyzer(taxonomy)
recommender = RecommenderEngine(analyzer, taxonomy)
recommender.set_candidate_pool(data_loader.candidate_reels)
evaluator = BenchmarkEvaluator(DATA_DIR)
supabase_adapter = SupabaseClientAdapter()

# In-memory user graphs cache: user_id -> UserInterestGraph
user_graphs: Dict[str, UserInterestGraph] = {}


def get_or_create_user_graph(user_id: str) -> UserInterestGraph:
    """Gets or initializes a user's latent interest graph from their history."""
    if user_id in user_graphs:
        return user_graphs[user_id]

    user_info = data_loader.users.get(user_id, {})
    primary_lang = user_info.get("primary_language_pref", "English")
    graph = UserInterestGraph(user_id=user_id, primary_lang=primary_lang, taxonomy=taxonomy)

    # Ingest historical interactions
    interactions = data_loader.get_user_interactions(user_id)
    interactions.sort(key=lambda x: x.get("timestamp", ""))

    for inter in interactions:
        rid = inter.get("reel_id")
        reel = data_loader.get_reel(rid)
        if reel:
            analysis = analyzer.extract_layers(reel)
            graph.process_interaction(inter, analysis)

    user_graphs[user_id] = graph
    return graph


# --- Pydantic Models ---

class InteractionRequest(BaseModel):
    user_id: str
    reel_id: str
    watch_percentage: float = Field(..., ge=0.0, le=100.0)
    watch_seconds: Optional[float] = 0.0
    liked: int = 0
    saved: int = 0
    shared: int = 0
    replayed: int = 0
    skipped: int = 0
    followed_creator: int = 0


class RecommendRequest(BaseModel):
    user_id: str
    current_reel_id: str


class FeedbackRequest(BaseModel):
    user_id: str
    feedback_type: str = Field(..., description="useful | not_useful | more_like_this | dont_show_topic | prefer_language")
    topic_or_category: str
    detail: Optional[str] = None


class SupabaseConfigRequest(BaseModel):
    supabase_url: str
    supabase_key: str


# --- API Routes ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_reels": len(data_loader.reels_list),
        "total_users": len(data_loader.users),
        "candidate_pool_size": len(data_loader.candidate_reels),
        "categories": VALID_CATEGORIES,
        "supabase_connected": supabase_adapter.is_connected
    }


@app.get("/api/users")
def list_users(limit: int = 500, filter_traps_first: bool = True):
    """Returns users with persona metadata. Traps and special users appear at top."""
    all_users = data_loader.get_all_users()
    
    # Sort traps to top
    trap_ids = ["TRAP_JAVA_BACKEND", "TRAP_MULTILINGUAL", "TRAP_ENTERTAINMENT_HEAVY"]
    traps = [u for u in all_users if u["user_id"] in trap_ids]
    others = [u for u in all_users if u["user_id"] not in trap_ids]

    ordered = (traps + others) if filter_traps_first else all_users
    return {
        "total": len(all_users),
        "users": ordered[:limit]
    }


@app.get("/api/users/{user_id}")
def get_user_profile(user_id: str):
    """Returns detailed user metadata, ground truth (if available), and stats."""
    user = data_loader.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    graph = get_or_create_user_graph(user_id)
    gt = data_loader.ground_truth.get(user_id, {})
    
    return {
        "user": user,
        "ground_truth": gt,
        "confidence": graph.get_confidence_level(),
        "top_inferred_interests": graph.get_top_inferred_interests(4),
        "interaction_count": graph.interaction_count,
        "language_preferences": graph.language_weights,
        "progression_stage": recommender.determine_student_progression_stage(graph)
    }


@app.get("/api/users/{user_id}/graph")
def get_user_interest_graph(user_id: str):
    """Returns the visual node-edge graph data for the frontend canvas."""
    graph = get_or_create_user_graph(user_id)
    return graph.to_graph_data()


@app.get("/api/users/{user_id}/feed")
def get_user_feed(user_id: str, limit: int = 25):
    """Returns the scrollable reel feed for a user, including history & new candidate reels."""
    graph = get_or_create_user_graph(user_id)
    
    # Build personalized mixture with full history
    history_interactions = data_loader.get_user_interactions(user_id)
    history_reels = []
    for inter in history_interactions:
        r = data_loader.get_reel(inter.get("reel_id"))
        if r:
            enriched = dict(r)
            enriched["_user_interaction"] = inter
            history_reels.append(enriched)

    # Next candidate reels
    candidate_feed = []
    for c in data_loader.candidate_reels[:limit]:
        analysis = analyzer.extract_layers(c)
        cand_dict = dict(c)
        cand_dict["_analysis"] = analysis
        candidate_feed.append(cand_dict)

    return {
        "user_id": user_id,
        "history_reels": history_reels,
        "feed_reels": candidate_feed,
        "total_feed": len(history_reels) + len(candidate_feed)
    }


@app.get("/api/reels/{reel_id}")
def get_reel_details(reel_id: str):
    """Returns full reel metadata and 4-layer multimodal analysis."""
    reel = data_loader.get_reel(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    analysis = analyzer.extract_layers(reel)
    return {
        "reel": reel,
        "analysis": analysis
    }


@app.post("/api/interact")
def record_interaction(interaction: InteractionRequest):
    """Records a live viewing interaction and immediately updates the latent interest graph."""
    graph = get_or_create_user_graph(interaction.user_id)
    reel = data_loader.get_reel(interaction.reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    analysis = analyzer.extract_layers(reel)
    inter_dict = interaction.model_dump()
    inter_dict["timestamp"] = datetime.now().isoformat()
    inter_dict["interaction_id"] = f"LIVE_{int(datetime.now().timestamp() * 1000)}"

    graph.process_interaction(inter_dict, analysis)
    supabase_adapter.sync_user_interaction(inter_dict)

    # Get updated top interests and confidence
    return {
        "status": "success",
        "user_id": interaction.user_id,
        "reel_id": interaction.reel_id,
        "interaction_count": graph.interaction_count,
        "confidence": graph.get_confidence_level(),
        "top_interests": graph.get_top_inferred_interests(3),
        "graph_nodes_count": len(graph.entity_scores)
    }


@app.post("/api/recommend")
def get_recommendation(req: RecommendRequest):
    """
    Generates a personalized recommendation with the EXACT Part A.9 schema and explainability.
    """
    graph = get_or_create_user_graph(req.user_id)
    current_reel = data_loader.get_reel(req.current_reel_id)
    if not current_reel:
        # Fallback if unknown reel
        current_reel = {
            "reel_id": req.current_reel_id,
            "title": "Software Developer Video",
            "category": "tech_educational",
            "topics": "Software Engineering",
            "difficulty": "Intermediate"
        }

    rec_result = recommender.generate_recommendation(graph, current_reel)
    return rec_result


@app.post("/api/feedback")
def submit_feedback(fb: FeedbackRequest):
    """Applies user feedback directly into the interest graph."""
    graph = get_or_create_user_graph(fb.user_id)
    graph.apply_feedback(fb.feedback_type, fb.topic_or_category, fb.detail)
    
    fb_dict = fb.model_dump()
    fb_dict["timestamp"] = datetime.now().isoformat()
    supabase_adapter.sync_feedback(fb_dict)

    return {
        "status": "feedback_applied",
        "user_id": fb.user_id,
        "feedback_type": fb.feedback_type,
        "topic": fb.topic_or_category,
        "top_interests_after_feedback": graph.get_top_inferred_interests(3)
    }


@app.get("/api/benchmark/traps")
def run_benchmark_traps():
    """Runs automated evaluation on all 3 built-in traps and curiosity pairs."""
    report = evaluator.run_all_traps()
    return report


@app.get("/api/taxonomy/stages")
def get_progression_stages():
    """Returns learning journey stages and valid categories."""
    return {
        "stages": LEARNING_JOURNEY_STAGES,
        "categories": VALID_CATEGORIES
    }


@app.post("/api/supabase/config")
def configure_supabase(config: SupabaseConfigRequest):
    """Sets Supabase credentials and tests cloud connection."""
    res = supabase_adapter.set_credentials(config.supabase_url, config.supabase_key)
    return res


@app.get("/api/supabase/status")
def get_supabase_status():
    """Returns current Supabase status."""
    return supabase_adapter.get_status()
