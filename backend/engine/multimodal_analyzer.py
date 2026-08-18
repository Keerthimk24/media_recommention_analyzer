"""
backend/engine/multimodal_analyzer.py

4-Layer Multimodal Content Understanding Engine:
Layer 1: Raw Content (Topic, Visuals, Subtitles/OCR, Duration)
Layer 2: Tech Entities (Open-ended extraction: Languages, Frameworks, Concepts, Domains)
Layer 3: Human Speaking Language (Strictly decoupled from Programming Language)
Layer 4: Intent Classification (Education, Entertainment, Career, Meme, News, Hype)
+ Hybrid Hype/Clickbait Detector & Quality Rubric Scorer.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from .taxonomy import (
    PROGRAMMING_LANGUAGES,
    FRAMEWORKS,
    TECHNOLOGIES,
    CONCEPTS,
    DOMAINS,
    HUMAN_LANGUAGES,
    TaxonomyGraph
)

# Known Hype & Clickbait Patterns (Part A.6 / Part C)
HYPE_PATTERNS = [
    r"guarantee[d]?\s+(you\s+a\s+)?job",
    r"in\s+(just\s+)?\d+\s+(days|hours)",
    r"make\s+you\s+₹?\d+\s*lpa",
    r"this\s+one\s+skill\s+will\s+make\s+you",
    r"replace\s+(every\s+)?programmer",
    r"learn\s+everything\s+about\s+.*in\s+\d+\s+hours",
    r"jobless\s+by\s+\d{4}",
    r"top\s+secret\s+ai\s+trick",
    r"earn\s+\$\d+k\s+per\s+month\s+with\s+ai",
    r"no\s+experience\s+needed.*become\s+an\s+ai\s+engineer",
    r"secret\s+formula\s+to\s+crack\s+faang"
]

# Educational indicator keywords
EDUCATIONAL_PATTERNS = [
    r"how\s+to", r"deep\s+dive", r"understanding", r"architecture",
    r"under\s+the\s+hood", r"explained", r"system\s+design", r"internals",
    r"best\s+practices", r"benchmarking", r"step\s+by\s+step", r"tutorial",
    r"algorithm", r"memory\s+management", r"concurrency", r"microservices"
]

# Entertainment & Meme indicators
ENTERTAINMENT_PATTERNS = [
    r"meme", r"funny", r"comedy", r"relatable", r"when\s+you", r"pov:",
    r"junior\s+vs\s+senior", r"lifestyle", r"day\s+in\s+the\s+life", r"gaming",
    r"streamer", r"vlog", r"movie", r"cricket", r"celebrity"
]


class MultimodalAnalyzer:
    """Analyzes Reels across all 4 multimodal layers."""

    def __init__(self, taxonomy: Optional[TaxonomyGraph] = None):
        self.taxonomy = taxonomy or TaxonomyGraph()
        self._compile_regexes()

    def _compile_regexes(self):
        self.hype_regex = [re.compile(p, re.IGNORECASE) for p in HYPE_PATTERNS]
        self.edu_regex = [re.compile(p, re.IGNORECASE) for p in EDUCATIONAL_PATTERNS]
        self.ent_regex = [re.compile(p, re.IGNORECASE) for p in ENTERTAINMENT_PATTERNS]

    def extract_layers(self, reel: Dict) -> Dict:
        """
        Extracts 4-layer understanding from a reel dictionary.
        """
        title = reel.get("title", "")
        caption = reel.get("caption", "")
        transcript = reel.get("transcript", "")
        ocr_text = reel.get("ocr_text", "")
        vis_desc = reel.get("visual_description", "")
        hashtags = reel.get("hashtags", "")
        
        full_text = f"{title} {caption} {transcript} {ocr_text} {vis_desc} {hashtags}"

        # Layer 1: Raw Content
        raw_content = {
            "title": title,
            "duration_seconds": float(reel.get("duration_seconds", 30)),
            "visual_description": vis_desc,
            "has_code_visual": any(w in vis_desc.lower() for w in ["code", "ide", "vscode", "terminal", "editor", "whiteboard", "diagram"]),
            "has_face_visual": "talking" in vis_desc.lower() or "person" in vis_desc.lower() or "presenter" in vis_desc.lower()
        }

        # Layer 2: Tech Entities (Open-ended detection)
        tech_entities = self.extract_tech_entities(full_text, reel)

        # Layer 3: Human Speaking Language (Strictly decoupled from Programming Language)
        human_language = self.detect_human_language(reel)

        # Layer 4: Intent Classification & Hype Score
        intent, hype_score, quality_score = self.classify_intent_and_quality(reel, full_text)

        # Canonical category mapping (Part A.9 Category enum)
        category_enum = self.taxonomy.map_to_category_enum(
            topics=reel.get("topics", ""),
            prog_langs=reel.get("programming_languages", ""),
            techs=reel.get("technologies", ""),
            frameworks=reel.get("frameworks", ""),
            title=title
        )

        return {
            "reel_id": reel.get("reel_id", ""),
            "raw_content": raw_content,
            "tech_entities": tech_entities,
            "human_language": human_language,
            "intent": intent,
            "category_enum": category_enum,
            "hype_score": hype_score,
            "quality_score": quality_score,
            "difficulty": reel.get("difficulty", "Intermediate"),
            "learning_value": float(reel.get("learning_value", quality_score * 0.9)),
            "career_value": float(reel.get("career_value", 0.5))
        }

    def extract_tech_entities(self, text: str, reel: Dict) -> Dict[str, List[str]]:
        """
        Extracts programming languages, frameworks, technologies, concepts, and domains.
        Generalizes to unseen tools via keyword matching and heuristics.
        """
        text_lower = text.lower()
        extracted_langs = set()
        extracted_frameworks = set()
        extracted_techs = set()
        extracted_concepts = set()
        extracted_domains = set()

        # Seed from reel existing metadata if available
        if reel.get("programming_languages"):
            for lang in reel["programming_languages"].split(","):
                if lang.strip():
                    extracted_langs.add(lang.strip())
        if reel.get("technologies"):
            for t in reel["technologies"].split(","):
                if t.strip():
                    extracted_techs.add(t.strip())
        if reel.get("frameworks"):
            for f in reel["frameworks"].split(","):
                if f.strip():
                    extracted_frameworks.add(f.strip())
        if reel.get("topics"):
            for top in reel["topics"].split(","):
                if top.strip():
                    extracted_domains.add(top.strip())

        # Title and text explicit concept matching
        title = reel.get("title", "")
        title_lower = title.lower()
        if any(w in title_lower for w in ["backend", "rate limit", "scalable", "architecture", "microservices"]):
            extracted_concepts.add("Backend")
            extracted_concepts.add("System Design")
            extracted_domains.add("Backend")
        if any(w in title_lower for w in ["load balancer", "load balancing"]):
            extracted_concepts.add("Load Balancing")
            extracted_concepts.add("HLD")
            extracted_concepts.add("System Design")
        if any(w in title_lower for w in ["database", "indexes", "sql", "queries"]):
            extracted_concepts.add("Databases")
            extracted_concepts.add("Backend")
        if any(w in title_lower for w in ["system design", "url shortener", "consistent hashing"]):
            extracted_concepts.add("System Design")
            extracted_concepts.add("HLD")
            extracted_concepts.add("Distributed Systems")
        if any(w in title_lower for w in ["api", "rest", "graphql"]):
            extracted_concepts.add("APIs")
            extracted_concepts.add("REST")
        if any(w in title_lower for w in ["vector database", "ml api", "deploy models", "machine learning"]):
            extracted_domains.add("AI/ML")
            extracted_concepts.add("AI/ML")
        if any(w in title_lower for w in ["dsa", "algorithms", "data structures"]):
            extracted_concepts.add("DSA")
            extracted_domains.add("DSA")

        for fw in FRAMEWORKS:
            pattern = rf"\b{re.escape(fw.lower())}\b"
            if re.search(pattern, text_lower):
                extracted_frameworks.add(fw)

        for tech in TECHNOLOGIES:
            pattern = rf"\b{re.escape(tech.lower())}\b"
            if re.search(pattern, text_lower):
                extracted_techs.add(tech)

        for concept in CONCEPTS:
            pattern = rf"\b{re.escape(concept.lower())}\b"
            if re.search(pattern, text_lower):
                extracted_concepts.add(concept)

        for domain in DOMAINS:
            pattern = rf"\b{re.escape(domain.lower())}\b"
            if re.search(pattern, text_lower):
                extracted_domains.add(domain)

        return {
            "programming_languages": sorted(list(extracted_langs)),
            "frameworks": sorted(list(extracted_frameworks)),
            "technologies": sorted(list(extracted_techs)),
            "concepts": sorted(list(extracted_concepts)),
            "domains": sorted(list(extracted_domains))
        }

    def detect_human_language(self, reel: Dict) -> Dict[str, str]:
        """
        Determines the spoken/human language separately from code.
        Example: "Telugu explanation of Python code" ->
        content_language: "Telugu", programming_language: "Python".
        """
        raw_lang = reel.get("content_language", "English").strip()
        confidence = float(reel.get("language_confidence", 0.95))

        # Check if code-switched / mixed
        is_mixed = "-" in raw_lang or "mixed" in raw_lang.lower()
        base_lang = raw_lang.split("-")[0] if is_mixed else raw_lang

        return {
            "content_language": raw_lang,
            "base_language": base_lang,
            "is_code_switched": is_mixed,
            "confidence": confidence
        }

    def classify_intent_and_quality(self, reel: Dict, full_text: str) -> Tuple[str, float, float]:
        """
        Classifies intent and computes quality and hype scores.
        """
        # Base hype estimation
        hype_matches = sum(1 for reg in self.hype_regex if reg.search(full_text))
        hype_from_text = min(1.0, hype_matches * 0.35)

        category = reel.get("category", "").lower()
        intent = reel.get("intent", "").capitalize()

        if not intent:
            if category == "hype" or hype_from_text > 0.4:
                intent = "Hype"
            elif category == "programming_meme" or any(r.search(full_text) for r in self.ent_regex):
                intent = "Meme"
            elif category == "entertainment":
                intent = "Entertainment"
            elif category == "career":
                intent = "Career"
            elif any(r.search(full_text) for r in self.edu_regex) or category == "tech_educational":
                intent = "Education"
            else:
                intent = "Education"

        # Blend with precomputed scores from dataset if available
        hype_score = float(reel.get("hype_score", hype_from_text))
        if category == "hype":
            hype_score = max(hype_score, 0.85)

        raw_quality = float(reel.get("quality_score", 0.7))
        # Content Quality Score Formula (Part A.6):
        # Educational Value + Tech Depth + Credibility + Practicality - Hype
        quality_score = max(0.05, min(0.99, raw_quality * (1.0 - (hype_score * 0.4))))

        return intent, round(hype_score, 3), round(quality_score, 3)
