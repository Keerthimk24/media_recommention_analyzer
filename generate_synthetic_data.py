"""
generate_synthetic_data.py

Generates a fully synthetic, anonymized dataset for the Reels
interest-inference / tech-recommendation agent, per the mandatory
synthetic-data spec. No real social-media data is used or required.

Usage:
    python generate_synthetic_data.py            # full scale
    python generate_synthetic_data.py --demo      # lightweight dev mode
    python generate_synthetic_data.py --seed 7     # different seed
"""

import argparse
import csv
import json
import os
import random
import sys
from datetime import datetime, timedelta

import numpy as np

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------

FULL_CONFIG = dict(NUM_REELS=5000, NUM_USERS=500, NUM_INTERACTIONS=50000,
                    NUM_CREATORS=100, NUM_CANDIDATE_REELS=800)
DEMO_CONFIG = dict(NUM_REELS=100, NUM_USERS=20, NUM_INTERACTIONS=1000,
                    NUM_CREATORS=20, NUM_CANDIDATE_REELS=80)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# --------------------------------------------------------------------------
# TAXONOMY
# --------------------------------------------------------------------------

PROGRAMMING_LANGUAGES = ["Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
                          "Go", "Rust", "Kotlin", "Swift", "PHP", "Dart", "R", "SQL",
                          "Scala", "Ruby"]

FRAMEWORKS = ["React", "Angular", "Vue", "Spring Boot", "Django", "FastAPI", "Flask",
              "Express.js", ".NET", "Node.js", "TensorFlow", "PyTorch", "Next.js",
              "Svelte", "Laravel", "Ktor"]

TECHNOLOGIES = ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "PostgreSQL", "MongoDB",
                "Redis", "Git", "Jenkins", "Terraform", "Linux", "Kafka", "GraphQL",
                "Nginx", "Elasticsearch"]

CONCEPTS = ["DSA", "OOP", "APIs", "HLD", "LLD", "REST", "Microservices",
            "Distributed Systems", "System Design", "Databases", "Data Structures",
            "Algorithms", "Design Patterns", "Concurrency", "Memory Management",
            "Caching", "Load Balancing"]

DOMAINS = ["AI/ML", "Deep Learning", "Generative AI", "Cloud", "DevOps",
           "Cybersecurity", "Networking", "Web Development", "Mobile Development",
           "Backend", "Frontend", "Software Engineering", "Career", "Hardware",
           "Data Science", "Blockchain"]

TECH_TYPE_LISTS = {
    "programming_language": PROGRAMMING_LANGUAGES,
    "framework": FRAMEWORKS,
    "technology": TECHNOLOGIES,
    "concept": CONCEPTS,
    "domain": DOMAINS,
}

HUMAN_LANGUAGES = ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam", "Bengali"]
MIXED_LANGUAGES = ["Telugu-English", "Hindi-English", "Tamil-English", "Kannada-English"]

ENTERTAINMENT_TOPICS = ["Comedy", "Movies", "Cricket", "Football", "Gaming", "Music",
                         "Memes", "Lifestyle", "Celebrity Fiction"]

CAREER_TOPICS = ["Coding Interviews", "Resume Tips", "Placement Prep",
                  "Internship Advice", "Technical Interviews", "Career Roadmaps",
                  "Software Engineering Careers"]

TECH_NEWS_TOPICS = ["AI News", "Programming Language Updates", "Cloud News",
                     "Hardware Launches", "Developer Tools", "Cybersecurity News"]

HYPE_TEMPLATES = [
    "10 AI tools that will GUARANTEE you a job in {year}!!!",
    "Become an AI Engineer in just 7 days - no experience needed!",
    "This ONE skill will make you \u20b950 LPA, guaranteed!",
    "Learn EVERYTHING about coding in 24 hours!",
    "5 tools that will REPLACE every programmer by {year}",
    "You NEED to learn this or you'll be jobless by {year}",
    "Top secret AI trick recruiters don't want you to know",
]

LEGIT_TECH_TITLES = [
    "How Backend Systems Handle 1 Million Requests",
    "Understanding Vector Databases",
    "Building a Production ML API",
    "How ML Engineers Deploy Models",
    "Designing a Scalable Backend API: From Code to Cloud",
    "Why Rust's Ownership Model Prevents Memory Bugs",
    "How Load Balancers Actually Work",
    "REST vs GraphQL: What to Use When",
    "Explaining Consistent Hashing",
    "How Kubernetes Schedules Pods",
    "System Design: Designing a URL Shortener",
    "How Database Indexes Speed Up Queries",
]

PERSONAS = {
    "backend_focused": {
        "weights": {"Java": 0.20, "Spring Boot": 0.15, "REST": 0.10, "AWS": 0.12,
                    "Docker": 0.10, "System Design": 0.13, "DSA": 0.10, "entertainment": 0.10},
        "primary": "Backend Engineering",
    },
    "ai_focused": {
        "weights": {"Python": 0.20, "AI/ML": 0.18, "Deep Learning": 0.12, "PyTorch": 0.10,
                    "TensorFlow": 0.10, "Generative AI": 0.10, "DSA": 0.08, "entertainment": 0.12},
        "primary": "AI / Machine Learning",
    },
    "cybersecurity_focused": {
        "weights": {"Linux": 0.18, "Networking": 0.15, "Cybersecurity": 0.25,
                    "Cloud": 0.10, "Web Development": 0.07, "entertainment": 0.10, "Python": 0.15},
        "primary": "Cybersecurity",
    },
    "frontend_focused": {
        "weights": {"JavaScript": 0.20, "React": 0.18, "TypeScript": 0.12, "CSS": 0.10,
                    "Web Development": 0.12, "entertainment": 0.13, "UI/UX": 0.15},
        "primary": "Frontend / Web Development",
    },
    "hardware_focused": {
        "weights": {"Hardware": 0.28, "GPUs": 0.15, "Laptops": 0.12, "CPUs": 0.10,
                    "AI/ML": 0.10, "Gaming": 0.15, "entertainment": 0.10},
        "primary": "Hardware / Developer Gear",
    },
    "entertainment_heavy": {
        "weights": {"Comedy": 0.25, "Movies": 0.20, "Sports": 0.15, "Gaming": 0.15,
                    "Music": 0.10, "entertainment": 0.15},
        "primary": "Entertainment",
    },
    "mixed_interest": {
        "weights": {"Java": 0.10, "Python": 0.10, "AI/ML": 0.10, "Cloud": 0.08,
                    "DSA": 0.10, "Career": 0.10, "Cybersecurity": 0.07, "entertainment": 0.35},
        "primary": "Mixed Technology Interests",
    },
}
PERSONA_SAMPLE_WEIGHTS = [0.18, 0.16, 0.10, 0.14, 0.08, 0.14, 0.20]

FIRST_NAMES = ["Aarav", "Vihaan", "Ishaan", "Meera", "Ananya", "Kavya", "Rohan", "Neha",
               "Sai", "Priya", "Arjun", "Divya", "Karthik", "Sneha", "Vikram", "Pooja",
               "Rahul", "Anjali", "Suresh", "Lakshmi"]
LAST_NAMES = ["Rao", "Reddy", "Sharma", "Kumar", "Iyer", "Nair", "Patel", "Gupta",
              "Menon", "Chowdhury", "Verma", "Naidu"]

random.seed(0)


# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------

def rid(prefix, n):
    return f"{prefix}{n:06d}"


def random_timestamp(start, end):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def noisy(val, spread=0.08):
    return clamp(val + np.random.normal(0, spread))


# --------------------------------------------------------------------------
# CREATORS
# --------------------------------------------------------------------------

def generate_creators(n):
    creators = []
    handles_used = set()
    all_topics = PROGRAMMING_LANGUAGES + FRAMEWORKS + TECHNOLOGIES + CONCEPTS + DOMAINS + ENTERTAINMENT_TOPICS
    for i in range(n):
        cid = rid("CR", i + 1)
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        handle = f"{fname.lower()}.{lname.lower()}{random.randint(1,999)}"
        while handle in handles_used:
            handle = f"{fname.lower()}.{lname.lower()}{random.randint(1,999)}"
        handles_used.add(handle)
        n_topics = random.randint(1, 3)
        primary_topics = random.sample(all_topics, n_topics)
        language = random.choice(HUMAN_LANGUAGES + MIXED_LANGUAGES)
        # deliberately decorrelate quality vs engagement vs credibility
        technical_quality = round(np.random.beta(2, 2), 3)
        educational_value = round(clamp(noisy(technical_quality, 0.15)), 3)
        credibility_score = round(clamp(noisy(technical_quality, 0.20)), 3)
        average_engagement = round(np.random.beta(2, 3), 3)
        creators.append(dict(
            creator_id=cid, creator_name=f"{fname} {lname}", handle=handle,
            primary_topics="|".join(primary_topics), language=language,
            technical_quality=technical_quality, educational_value=educational_value,
            credibility_score=credibility_score, average_engagement=average_engagement,
        ))
    return creators


# --------------------------------------------------------------------------
# TECHNOLOGY ENTITIES + KNOWLEDGE GRAPH
# --------------------------------------------------------------------------

def generate_technologies():
    rows = []
    seen = set()
    for ttype, items in TECH_TYPE_LISTS.items():
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            rows.append(dict(entity_id=f"T{len(rows)+1:04d}", entity_name=item, entity_type=ttype))
    # pad toward 500+ entities with realistic versioned/derived variants
    variant_suffixes = ["Fundamentals", "Advanced", "for Beginners", "Best Practices",
                         "in Production", "Interview Questions", "Design Patterns",
                         "Performance Tuning", "Security", "Testing"]
    base_names = [r["entity_name"] for r in rows]
    idx = len(rows) + 1
    while len(rows) < 520:
        base = random.choice(base_names)
        suffix = random.choice(variant_suffixes)
        name = f"{base} {suffix}"
        if name in seen:
            continue
        seen.add(name)
        rows.append(dict(entity_id=f"T{idx:04d}", entity_name=name, entity_type="sub_topic"))
        idx += 1
    return rows


CURATED_RELATIONSHIPS = [
    ("Python", "related_to", "AI/ML", "Beginner", 0.9),
    ("Python", "related_to", "Data Science", "Beginner", 0.85),
    ("Python", "related_to", "Backend", "Beginner", 0.7),
    ("Java", "related_to", "Spring Boot", "Intermediate", 0.85),
    ("Java", "related_to", "Backend", "Beginner", 0.8),
    ("Java", "related_to", "Android", "Intermediate", 0.6),
    ("Spring Boot", "related_to", "Backend", "Intermediate", 0.85),
    ("REST", "prerequisite_for", "Microservices", "Intermediate", 0.8),
    ("Docker", "related_to", "DevOps", "Intermediate", 0.8),
    ("Docker", "prerequisite_for", "Kubernetes", "Intermediate", 0.75),
    ("AWS", "related_to", "Cloud", "Intermediate", 0.9),
    ("AWS", "related_to", "Backend", "Intermediate", 0.6),
    ("System Design", "related_to", "Backend", "Advanced", 0.9),
    ("System Design", "related_to", "HLD", "Advanced", 0.9),
    ("DSA", "prerequisite_for", "System Design", "Intermediate", 0.7),
    ("DSA", "related_to", "Coding Interviews", "Beginner", 0.9),
    ("JavaScript", "related_to", "React", "Beginner", 0.85),
    ("React", "related_to", "Frontend", "Intermediate", 0.85),
    ("TypeScript", "related_to", "JavaScript", "Intermediate", 0.7),
    ("Rust", "related_to", "Memory Management", "Advanced", 0.8),
    ("Rust", "related_to", "Systems Programming", "Advanced", 0.85),
    ("Kubernetes", "related_to", "Cloud", "Advanced", 0.75),
    ("Cybersecurity", "related_to", "Networking", "Intermediate", 0.75),
    ("Linux", "prerequisite_for", "Cybersecurity", "Beginner", 0.7),
    ("Machine Learning", "related_to", "Deep Learning", "Intermediate", 0.8),
    ("Deep Learning", "related_to", "Generative AI", "Advanced", 0.75),
    ("SQL", "related_to", "Databases", "Beginner", 0.8),
    ("Databases", "related_to", "Backend", "Intermediate", 0.7),
    ("GPUs", "related_to", "AI/ML", "Intermediate", 0.6),
    ("Hardware", "related_to", "GPUs", "Beginner", 0.6),
]


def generate_technology_relationships(target=120):
    rows = []
    for i, (s, rel, t, diff, career) in enumerate(CURATED_RELATIONSHIPS):
        rows.append(dict(rel_id=f"REL{i+1:04d}", source=s, relationship=rel, target=t,
                          difficulty=diff, career_relevance=career))
    all_entities = list(set(PROGRAMMING_LANGUAGES + FRAMEWORKS + TECHNOLOGIES + CONCEPTS + DOMAINS))
    idx = len(rows) + 1
    rel_types = ["related_to", "prerequisite_for", "used_with"]
    diffs = ["Beginner", "Intermediate", "Advanced"]
    seen_pairs = {(r["source"], r["target"]) for r in rows}
    while len(rows) < target:
        s, t = random.sample(all_entities, 2)
        if (s, t) in seen_pairs or s == t:
            continue
        seen_pairs.add((s, t))
        rows.append(dict(rel_id=f"REL{idx:04d}", source=s, relationship=random.choice(rel_types),
                          target=t, difficulty=random.choice(diffs),
                          career_relevance=round(random.uniform(0.3, 0.95), 2)))
        idx += 1
    return rows


# --------------------------------------------------------------------------
# TRANSCRIPT / CAPTION / OCR / VISUAL TEMPLATE GENERATION
# --------------------------------------------------------------------------

def gen_transcript(category, prog_langs, content_lang, difficulty):
    lang_prefixes = {
        "Telugu-English": "Ee video lo manam {topic} gurinchi chuddam. ",
        "Hindi-English": "Aaj hum dekhenge ki {topic} kaise kaam karta hai. ",
        "Tamil-English": "Indha video la naam {topic} pathi parkalam. ",
        "Kannada-English": "Ee video alli navu {topic} bagge nodona. ",
    }
    topic = prog_langs[0] if prog_langs else random.choice(CONCEPTS + DOMAINS)

    if category == "hype":
        return random.choice(HYPE_TEMPLATES).format(year=random.choice([2026, 2027]))

    if category == "meme":
        return (f"When your {topic} code works on the first try but you have no idea why. "
                f"Every developer knows this feeling.")

    body_en = {
        "Beginner": f"Let's break down the basics of {topic} step by step, starting from what it actually is.",
        "Intermediate": f"If you're preparing for placements, don't just memorize {topic} answers - "
                         f"understand how it actually works under the hood.",
        "Advanced": f"Here's how {topic} behaves at scale, and the trade-offs engineers make in production systems.",
    }[difficulty]

    if content_lang in lang_prefixes:
        prefix = lang_prefixes[content_lang].format(topic=topic)
        return prefix + f"First, {topic.lower()} basics, then a quick example with real code."
    return body_en


def gen_ocr(prog_langs):
    if not prog_langs or random.random() < 0.35:
        return ""
    snippets = {
        "Java": "public static void main(String[] args)",
        "Python": "def train_model(data): ...",
        "SQL": "SELECT * FROM students;",
        "JavaScript": "const res = await fetch('/api/data');",
        "Go": "func main() { fmt.Println(\"hello\") }",
        "Rust": "let mut v: Vec<i32> = Vec::new();",
        "C++": "int main() { std::cout << \"hi\"; }",
    }
    lang = random.choice(prog_langs)
    return snippets.get(lang, f"// {lang} example")


def gen_visual_description(category, prog_langs):
    if category == "entertainment":
        return random.choice([
            "Funny reaction clip with captions",
            "Stadium crowd celebrating a goal/wicket",
            "Dance/lipsync trend clip",
            "Movie clip montage with trending audio",
        ])
    if prog_langs:
        return random.choice([
            f"Laptop screen showing {prog_langs[0]} code in an IDE",
            f"Terminal window running {prog_langs[0]} commands",
            "Whiteboard diagram explaining system architecture",
            "Split-screen code and output comparison",
        ])
    return random.choice([
        "Person explaining AWS architecture using a whiteboard",
        "Gaming setup with GPU comparison on screen",
        "Cybersecurity terminal showing network commands",
        "Neural network diagram with labeled layers",
        "Two laptops side by side for a spec comparison",
    ])


# --------------------------------------------------------------------------
# REELS
# --------------------------------------------------------------------------

CATEGORY_WEIGHTS = {
    "entertainment": 0.28,
    "programming_meme": 0.12,
    "tech_educational": 0.30,
    "career": 0.10,
    "tech_news": 0.08,
    "hype": 0.12,
}


def pick_category():
    cats, weights = zip(*CATEGORY_WEIGHTS.items())
    return random.choices(cats, weights=weights, k=1)[0]


def pick_prog_langs():
    r = random.random()
    if r < 0.30:
        return []
    if r < 0.80:
        return [random.choice(PROGRAMMING_LANGUAGES)]
    n = random.choice([2, 2, 3])
    return random.sample(PROGRAMMING_LANGUAGES, n)


def pick_content_language():
    r = random.random()
    if r < 0.55:
        return "English"
    if r < 0.85:
        return random.choice(MIXED_LANGUAGES)
    return random.choice(HUMAN_LANGUAGES[1:])


def gen_reel(reel_num, creators, start_date, end_date, force_category=None):
    category = force_category or pick_category()
    prog_langs = pick_prog_langs() if category not in ("entertainment", "hype") else (
        pick_prog_langs() if random.random() < 0.4 else [])
    content_lang = pick_content_language()
    difficulty = random.choices(["Beginner", "Intermediate", "Advanced"], weights=[0.45, 0.4, 0.15])[0]

    if category == "entertainment":
        topic = random.choice(ENTERTAINMENT_TOPICS)
        title = f"{topic} moment that broke the internet"
        caption = f"{topic} content - just for laughs"
        intent = random.choice(["Entertainment", "Humor"])
        technologies_field = []
        frameworks_field = []
        domain = topic
    elif category == "programming_meme":
        topic = prog_langs[0] if prog_langs else "Programming"
        title = f"{topic} developers be like"
        caption = f"POV: debugging {topic} at 2am"
        intent = "Entertainment"
        technologies_field = []
        frameworks_field = []
        domain = "Software Engineering"
    elif category == "career":
        topic = random.choice(CAREER_TOPICS)
        title = topic
        caption = f"{topic} - what nobody tells you"
        intent = random.choice(["Career", "Interview Preparation", "Motivation"])
        technologies_field = []
        frameworks_field = []
        domain = "Career"
    elif category == "tech_news":
        topic = random.choice(TECH_NEWS_TOPICS)
        title = topic + f" update ({random.choice([2025,2026])})"
        caption = f"Latest in {topic}"
        intent = "News"
        technologies_field = random.sample(TECHNOLOGIES, k=min(2, len(TECHNOLOGIES)))
        frameworks_field = []
        domain = "Technology News"
    elif category == "hype":
        title = random.choice(HYPE_TEMPLATES).format(year=random.choice([2026, 2027]))
        caption = title
        intent = random.choice(["Promotion", "Motivation"])
        technologies_field = []
        frameworks_field = []
        domain = "AI/ML" if "AI" in title else "Career"
        prog_langs = []
    else:  # tech_educational
        title = random.choice(LEGIT_TECH_TITLES) if random.random() < 0.3 else \
            f"{(prog_langs[0] if prog_langs else random.choice(CONCEPTS))} explained simply"
        caption = f"Learn {title.lower()} in under a minute"
        intent = random.choice(["Learning", "Project Help", "Curiosity", "Interview Preparation"])
        technologies_field = random.sample(TECHNOLOGIES, k=random.choice([0, 0, 1, 2]))
        frameworks_field = random.sample(FRAMEWORKS, k=random.choice([0, 1]))
        domain = random.choice(DOMAINS)

    transcript = gen_transcript(
        "hype" if category == "hype" else ("meme" if category == "programming_meme" else "edu"),
        prog_langs, content_lang, difficulty)
    ocr_text = gen_ocr(prog_langs)
    visual_description = gen_visual_description(
        "entertainment" if category == "entertainment" else "tech", prog_langs)

    if category == "hype":
        hype_score = round(np.random.beta(6, 2), 3)
        quality_score = round(clamp(np.random.beta(2, 4) + np.random.normal(0, 0.1)), 3)
    elif category in ("tech_educational", "career"):
        hype_score = round(np.random.beta(2, 6), 3)
        quality_score = round(np.random.beta(4, 2), 3)
    else:
        hype_score = round(np.random.beta(2, 5), 3)
        quality_score = round(np.random.beta(3, 3), 3)

    learning_value = round(clamp(noisy(quality_score if category == "tech_educational" else 0.2)), 3)
    career_value = round(clamp(noisy(0.7 if category == "career" else (0.5 if category == "tech_educational" else 0.15))), 3)
    practical_value = round(clamp(noisy(quality_score * 0.8)), 3)
    entertainment_value = round(clamp(noisy(0.85 if category in ("entertainment", "programming_meme") else 0.25)), 3)

    creator = random.choice(creators)

    return dict(
        reel_id=rid("RL", reel_num),
        title=title,
        caption=caption,
        transcript=transcript,
        ocr_text=ocr_text,
        visual_description=visual_description,
        content_language=content_lang,
        language_confidence=round(random.uniform(0.75, 0.99), 2),
        programming_languages="|".join(prog_langs),
        technologies="|".join(technologies_field),
        frameworks="|".join(frameworks_field),
        topics=domain,
        category=category,
        intent=intent,
        difficulty=difficulty,
        duration_seconds=random.randint(8, 90),
        creator_id=creator["creator_id"],
        created_at=random_timestamp(start_date, end_date).isoformat(),
        quality_score=quality_score,
        hype_score=hype_score,
        learning_value=learning_value,
        career_value=career_value,
        practical_value=practical_value,
        entertainment_value=entertainment_value,
    )


def generate_reels(n, creators, start_date, end_date):
    return [gen_reel(i + 1, creators, start_date, end_date) for i in range(n)]


def generate_candidate_reels(n, creators, start_date, end_date):
    """Separate recommendation pool: must include explicit hype vs legit contrast,
    varied difficulty/language/quality, and some duplicates of themes (not exact dupes)."""
    rows = generate_reels(n, creators, start_date, end_date)
    # force in the explicit hype-trap contrast set (section 28)
    for title in HYPE_TEMPLATES[:3]:
        rows.append(gen_reel(len(rows) + 1, creators, start_date, end_date, force_category="hype"))
    for title in LEGIT_TECH_TITLES:
        r = gen_reel(len(rows) + 1, creators, start_date, end_date, force_category="tech_educational")
        r["title"] = title
        r["caption"] = f"Deep dive: {title.lower()}"
        rows.append(r)
    for i, r in enumerate(rows):
        r["reel_id"] = rid("CAND", i + 1)
    return rows


# --------------------------------------------------------------------------
# USERS
# --------------------------------------------------------------------------

def generate_users(n):
    users = []
    persona_names = list(PERSONAS.keys())
    for i in range(n):
        uid = rid("U", i + 1)
        persona = random.choices(persona_names, weights=PERSONA_SAMPLE_WEIGHTS, k=1)[0]
        weights = {k: clamp(noisy(v, 0.05)) for k, v in PERSONAS[persona]["weights"].items()}
        primary_lang = random.choices(HUMAN_LANGUAGES, weights=[0.4, 0.18, 0.15, 0.09, 0.08, 0.06, 0.04])[0]
        secondary_lang = random.choice([l for l in HUMAN_LANGUAGES if l != primary_lang])
        users.append(dict(
            user_id=uid,
            persona=persona,
            true_primary_interest=PERSONAS[persona]["primary"],
            interest_weights=json.dumps(weights),
            primary_language_pref=primary_lang,
            secondary_language_pref=secondary_lang,
            skill_level=random.choices(["Beginner", "Intermediate", "Advanced"], weights=[0.4, 0.4, 0.2])[0],
            joined_at=random_timestamp(datetime(2025, 1, 1), datetime(2025, 6, 1)).isoformat(),
        ))
    return users


def add_trap_users(users):
    """Sections 25-27: explicitly injected edge-case users."""
    trap_users = [
        dict(user_id="TRAP_JAVA_BACKEND", persona="backend_focused",
             true_primary_interest="Software Engineering / Backend",
             interest_weights=json.dumps({"Java": 0.22, "Spring Boot": 0.18, "REST": 0.12,
                                           "AWS": 0.14, "System Design": 0.14, "entertainment": 0.10,
                                           "hype_ai": -0.2}),
             primary_language_pref="English", secondary_language_pref="Hindi",
             skill_level="Intermediate", joined_at=datetime(2025, 2, 1).isoformat()),
        dict(user_id="TRAP_MULTILINGUAL", persona="ai_focused",
             true_primary_interest="AI / Machine Learning",
             interest_weights=json.dumps({"Python": 0.30, "AI/ML": 0.30, "Deep Learning": 0.15,
                                           "Backend": 0.10, "entertainment": 0.05}),
             primary_language_pref="Telugu", secondary_language_pref="English",
             skill_level="Beginner", joined_at=datetime(2025, 3, 1).isoformat()),
        dict(user_id="TRAP_ENTERTAINMENT_HEAVY", persona="mixed_interest",
             true_primary_interest="Programming / DSA (masked by heavy entertainment consumption)",
             interest_weights=json.dumps({"Comedy": 0.20, "Movies": 0.18, "Cricket": 0.17,
                                           "Java": 0.16, "Python": 0.15, "DSA": 0.14}),
             primary_language_pref="English", secondary_language_pref="Tamil",
             skill_level="Intermediate", joined_at=datetime(2025, 1, 15).isoformat()),
    ]
    return users + trap_users


# --------------------------------------------------------------------------
# GROUND TRUTH
# --------------------------------------------------------------------------

def generate_ground_truth(users):
    rows = []
    for u in users:
        weights = json.loads(u["interest_weights"])
        sorted_topics = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
        primary = u["true_primary_interest"]
        secondary = sorted_topics[1][0] if len(sorted_topics) > 1 else ""
        rows.append(dict(
            user_id=u["user_id"],
            true_primary_interest=primary,
            true_secondary_interest=secondary,
            true_language_preference=u["primary_language_pref"],
            true_skill_level=u["skill_level"],
        ))
    return rows


# --------------------------------------------------------------------------
# INTERACTIONS + SESSIONS
# --------------------------------------------------------------------------

def match_score(user, reel):
    weights = json.loads(user["interest_weights"])
    score = 0.0
    fields = (reel["topics"] + " " + reel["programming_languages"] + " " +
              reel["technologies"] + " " + reel["frameworks"] + " " + reel["category"])
    for topic, w in weights.items():
        if topic.lower() in fields.lower():
            score += w
    if reel["category"] in ("entertainment", "programming_meme"):
        score += weights.get("entertainment", 0.1)
    if reel["category"] == "hype":
        score += weights.get("hype_ai", 0.0)  # usually 0 or negative -> discourages hype
    lang_bonus = 0.15 if user["primary_language_pref"] in reel["content_language"] else 0.0
    return clamp(score + lang_bonus, -1, 1.5)


def simulate_engagement(score):
    """Turn a match score into noisy, non-deterministic engagement signals."""
    score = clamp(score, -1, 1.5)
    base = clamp((score + 1) / 2.5)  # roughly map to 0..1
    watch_pct = clamp(np.random.normal(base * 90, 15), 0, 100)
    liked = 1 if (watch_pct > 70 and random.random() < 0.55) else 0
    saved = 1 if (watch_pct > 80 and random.random() < 0.35) else 0
    shared = 1 if (watch_pct > 85 and random.random() < 0.15) else 0
    replayed = 1 if (watch_pct > 90 and random.random() < 0.3) else 0
    skipped = 1 if watch_pct < 25 else 0
    followed = 1 if (saved and random.random() < 0.1) else 0
    watch_seconds_ratio = watch_pct / 100
    return watch_pct, liked, saved, shared, replayed, skipped, followed, watch_seconds_ratio


SESSION_THEMES = ["entertainment_heavy", "dsa_java_interview", "ai_python", "gaming_hardware",
                  "cybersecurity", "backend_cloud", "mixed_scroll"]


def generate_interactions_and_sessions(n_target, users, reels, candidate_reels, start_date, end_date):
    interactions, sessions = [], []
    all_reels = reels + candidate_reels
    interaction_idx, session_idx = 1, 1

    max_rounds = 20  # safety cap against infinite loop
    round_num = 0
    while interaction_idx <= n_target and round_num < max_rounds:
        round_num += 1
        for u in users:
            n_sessions = random.randint(3, 8)
            for s in range(n_sessions):
                sid = rid("SESS", session_idx)
                session_idx += 1
                theme = random.choice(SESSION_THEMES)
                session_start = random_timestamp(start_date, end_date)
                n_reels_in_session = random.randint(3, 12)
                reels_in_session = random.sample(all_reels, min(n_reels_in_session, len(all_reels)))
                cursor = session_start
                session_watch_total = 0
                for r in reels_in_session:
                    score = match_score(u, r)
                    watch_pct, liked, saved, shared, replayed, skipped, followed, ratio = simulate_engagement(score)
                    watch_seconds = round(r["duration_seconds"] * ratio, 1)
                    cursor += timedelta(seconds=random.randint(2, 20) + int(watch_seconds))
                    interactions.append(dict(
                        interaction_id=rid("INT", interaction_idx),
                        user_id=u["user_id"], reel_id=r["reel_id"], timestamp=cursor.isoformat(),
                        session_id=sid, watch_seconds=watch_seconds,
                        watch_percentage=round(watch_pct, 1), liked=liked, saved=saved,
                        shared=shared, replayed=replayed, skipped=skipped, followed_creator=followed,
                    ))
                    interaction_idx += 1
                    session_watch_total += watch_seconds
                sessions.append(dict(
                    session_id=sid, user_id=u["user_id"], session_theme=theme,
                    start_time=session_start.isoformat(),
                    end_time=cursor.isoformat(),
                    reel_count=len(reels_in_session),
                    total_watch_seconds=round(session_watch_total, 1),
                ))
                if interaction_idx > n_target:
                    return interactions, sessions
    return interactions, sessions


def inject_curiosity_and_commitment(interactions, users, reels):
    """Section 19: explicitly add a curiosity sequence and a commitment sequence
    for a couple of sample users so both patterns exist in the data."""
    cyber_reels = [r for r in reels if "Cybersecurity" in r["topics"]][:4]
    if len(cyber_reels) < 4 or len(users) < 2:
        return interactions
    curiosity_user = users[0]["user_id"]
    commitment_user = users[1]["user_id"]
    base_time = datetime(2025, 6, 1)
    curiosity_pattern = [90, 20, 5]
    for i, pct in enumerate(curiosity_pattern):
        r = cyber_reels[i]
        interactions.append(dict(
            interaction_id=f"INT_CURIOSITY_{i}", user_id=curiosity_user, reel_id=r["reel_id"],
            timestamp=(base_time + timedelta(minutes=i)).isoformat(), session_id="SESS_CURIOSITY",
            watch_seconds=round(r["duration_seconds"] * pct / 100, 1), watch_percentage=pct,
            liked=0, saved=0, shared=0, replayed=0, skipped=1 if pct < 25 else 0, followed_creator=0,
        ))
    commitment_pattern = [94, 91, 97, 93]
    for i, pct in enumerate(commitment_pattern):
        r = cyber_reels[i]
        interactions.append(dict(
            interaction_id=f"INT_COMMITMENT_{i}", user_id=commitment_user, reel_id=r["reel_id"],
            timestamp=(base_time + timedelta(minutes=i)).isoformat(), session_id="SESS_COMMITMENT",
            watch_seconds=round(r["duration_seconds"] * pct / 100, 1), watch_percentage=pct,
            liked=1, saved=1 if i in (1, 2) else 0, shared=0, replayed=1 if i == 2 else 0,
            skipped=0, followed_creator=0,
        ))
    return interactions


def build_trap_histories(reels, candidate_reels):
    """Sections 25-27: explicit, hand-built interaction histories for the trap users,
    guaranteeing the exact scenario exists in the data regardless of random sampling."""
    def find_or_make(category, prog_lang=None, topic_contains=None, title=None, force_hype=False):
        pool = reels + candidate_reels
        for r in pool:
            if force_hype:
                if r["category"] != "hype":
                    continue
                return r
            if category and r["category"] != category:
                continue
            if prog_lang and prog_lang not in r["programming_languages"]:
                continue
            if topic_contains:
                haystack = (r["topics"] + " " + r.get("technologies", "") + " " +
                            r.get("frameworks", "") + " " + r.get("title", "")).lower()
                if topic_contains.lower() not in haystack:
                    continue
            return r
        return random.choice([r for r in pool if r["category"] == "hype"]) if force_hype else random.choice(reels)

    now = datetime(2025, 7, 1)
    interactions = []

    # --- TRAP_JAVA_BACKEND: Java meme, lifestyle, interview joke, laptop, SpringBoot/REST/AWS, AI hype skipped
    java_backend_reels = [
        find_or_make("programming_meme", prog_lang="Java"),
        find_or_make("career", topic_contains="Career"),
        find_or_make("programming_meme"),
        find_or_make("tech_educational", topic_contains="AWS"),
        find_or_make("tech_educational", topic_contains="Backend"),
        find_or_make(None, force_hype=True),
    ]
    engagements = [90, 88, 92, 85, 91, 3]  # last one (hype) is skipped
    for i, (r, pct) in enumerate(zip(java_backend_reels, engagements)):
        interactions.append(dict(
            interaction_id=f"INT_TRAPJB_{i}", user_id="TRAP_JAVA_BACKEND", reel_id=r["reel_id"],
            timestamp=(now + timedelta(minutes=i)).isoformat(), session_id="SESS_TRAP_JB",
            watch_seconds=round(r["duration_seconds"] * pct / 100, 1), watch_percentage=pct,
            liked=1 if pct > 70 else 0, saved=1 if pct > 85 else 0, shared=0,
            replayed=1 if i == 0 else 0, skipped=1 if pct < 25 else 0, followed_creator=0,
        ))

    # --- TRAP_MULTILINGUAL: Telugu Python/AI/ML, English backend, Hindi DSA
    multi_reels = [
        find_or_make("tech_educational", topic_contains="AI"),
        find_or_make("tech_educational", prog_lang="Python"),
        find_or_make("tech_educational"),
        find_or_make("tech_educational", topic_contains="Backend"),
        find_or_make("tech_educational", topic_contains="DSA"),
    ]
    for i, r in enumerate(multi_reels):
        pct = random.randint(80, 98)
        interactions.append(dict(
            interaction_id=f"INT_TRAPML_{i}", user_id="TRAP_MULTILINGUAL", reel_id=r["reel_id"],
            timestamp=(now + timedelta(minutes=i)).isoformat(), session_id="SESS_TRAP_ML",
            watch_seconds=round(r["duration_seconds"] * pct / 100, 1), watch_percentage=pct,
            liked=1, saved=1 if i % 2 == 0 else 0, shared=0, replayed=0, skipped=0, followed_creator=0,
        ))

    # --- TRAP_ENTERTAINMENT_HEAVY: Comedy/Movies/Cricket high engagement + Java/Python/DSA also high
    ent_reels = [find_or_make("entertainment") for _ in range(3)] + \
                [find_or_make("tech_educational", prog_lang="Java"),
                 find_or_make("tech_educational", prog_lang="Python"),
                 find_or_make("tech_educational", topic_contains="DSA")]
    for i, r in enumerate(ent_reels):
        pct = random.randint(90, 98)
        interactions.append(dict(
            interaction_id=f"INT_TRAPEH_{i}", user_id="TRAP_ENTERTAINMENT_HEAVY", reel_id=r["reel_id"],
            timestamp=(now + timedelta(minutes=i)).isoformat(), session_id="SESS_TRAP_EH",
            watch_seconds=round(r["duration_seconds"] * pct / 100, 1), watch_percentage=pct,
            liked=1, saved=1 if i >= 3 else 0, shared=0, replayed=1 if i == 5 else 0,
            skipped=0, followed_creator=0,
        ))

    return interactions


# --------------------------------------------------------------------------
# CSV / STATS
# --------------------------------------------------------------------------

def write_csv(path, rows):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_stats(users, reels, candidate_reels, interactions, creators, technologies, relationships):
    print("=" * 60)
    print("Synthetic Dataset Generated Successfully")
    print("=" * 60)
    print(f"Users: {len(users)}")
    print(f"Reels: {len(reels)}")
    print(f"Candidate Reels: {len(candidate_reels)}")
    print(f"Interactions: {len(interactions)}")
    print(f"Creators: {len(creators)}")
    print(f"Technology Entities: {len(technologies)}")
    print(f"Relationships: {len(relationships)}")

    print("\nLanguages:")
    lang_counts = {}
    for r in reels:
        lang_counts[r["content_language"]] = lang_counts.get(r["content_language"], 0) + 1
    for lang, count in sorted(lang_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {lang}: {count}")

    print("\nCategories:")
    cat_counts = {}
    for r in reels:
        cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
    for cat, count in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {cat}: {count}")

    hype_count = sum(1 for r in reels if r["hype_score"] > 0.6)
    high_quality_count = sum(1 for r in reels if r["quality_score"] > 0.7)
    print(f"\nHype Content (hype_score > 0.6): {hype_count}")
    print(f"High Quality Content (quality_score > 0.7): {high_quality_count}")
    print("=" * 60)


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Use lightweight demo-scale config")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default=OUT_DIR)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    cfg = DEMO_CONFIG if args.demo else FULL_CONFIG
    os.makedirs(args.out, exist_ok=True)

    start_date, end_date = datetime(2025, 1, 1), datetime(2025, 12, 1)

    creators = generate_creators(cfg["NUM_CREATORS"])
    technologies = generate_technologies()
    relationships = generate_technology_relationships()
    reels = generate_reels(cfg["NUM_REELS"], creators, start_date, end_date)
    candidate_reels = generate_candidate_reels(cfg["NUM_CANDIDATE_REELS"], creators, start_date, end_date)

    users = generate_users(cfg["NUM_USERS"])
    users = add_trap_users(users)
    ground_truth = generate_ground_truth(users)

    interactions, sessions = generate_interactions_and_sessions(
        cfg["NUM_INTERACTIONS"], users, reels, candidate_reels, start_date, end_date)
    interactions = inject_curiosity_and_commitment(interactions, users, reels)
    interactions += build_trap_histories(reels, candidate_reels)

    # strip helper-only field before writing users.csv
    users_out = [{k: v for k, v in u.items() if k != "interest_weights"} for u in users]

    write_csv(os.path.join(args.out, "users.csv"), users_out)
    write_csv(os.path.join(args.out, "reels.csv"), reels)
    write_csv(os.path.join(args.out, "candidate_reels.csv"), candidate_reels)
    write_csv(os.path.join(args.out, "interactions.csv"), interactions)
    write_csv(os.path.join(args.out, "sessions.csv"), sessions)
    write_csv(os.path.join(args.out, "creators.csv"), creators)
    write_csv(os.path.join(args.out, "technologies.csv"), technologies)
    write_csv(os.path.join(args.out, "technology_relationships.csv"), relationships)
    write_csv(os.path.join(args.out, "ground_truth.csv"), ground_truth)

    # keep full interest_weights (with hidden ground truth) in a separate file,
    # NOT to be used by the recommender at inference time
    with open(os.path.join(args.out, "_user_interest_weights_HIDDEN.json"), "w") as f:
        json.dump({u["user_id"]: json.loads(u["interest_weights"]) for u in users}, f, indent=2)

    print_stats(users, reels, candidate_reels, interactions, creators, technologies, relationships)
    print(f"\nFiles written to: {args.out}")
    print("NOTE: This is 100% synthetic/fictional data. No real user or creator data was used.")


if __name__ == "__main__":
    main()
