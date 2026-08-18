"""
backend/engine/taxonomy.py

Defines the technology taxonomy, entity classifications, hierarchical rollup relationships,
and canonical Category mapping according to Part A & Part B specifications.
"""

from typing import List, Dict, Set, Tuple, Optional
import csv
import os

# Canonical Category enum required by Part A.9
VALID_CATEGORIES = [
    "AI",
    "DSA",
    "Java",
    "HLD",
    "Cybersecurity",
    "Cloud",
    "Hardware",
    "Career",
    "Other"
]

# Base Entity definitions from Part B.1 / generator
PROGRAMMING_LANGUAGES = {
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
    "Go", "Rust", "Kotlin", "Swift", "PHP", "Dart", "R", "SQL",
    "Scala", "Ruby"
}

FRAMEWORKS = {
    "React", "Angular", "Vue", "Spring Boot", "Django", "FastAPI", "Flask",
    "Express.js", ".NET", "Node.js", "TensorFlow", "PyTorch", "Next.js",
    "Svelte", "Laravel", "Ktor"
}

TECHNOLOGIES = {
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "PostgreSQL", "MongoDB",
    "Redis", "Git", "Jenkins", "Terraform", "Linux", "Kafka", "GraphQL",
    "Nginx", "Elasticsearch"
}

CONCEPTS = {
    "DSA", "OOP", "APIs", "HLD", "LLD", "REST", "Microservices",
    "Distributed Systems", "System Design", "Databases", "Data Structures",
    "Algorithms", "Design Patterns", "Concurrency", "Memory Management",
    "Caching", "Load Balancing"
}

DOMAINS = {
    "AI/ML", "Deep Learning", "Generative AI", "Cloud", "DevOps",
    "Cybersecurity", "Networking", "Web Development", "Mobile Development",
    "Backend", "Frontend", "Software Engineering", "Career", "Hardware",
    "Data Science", "Blockchain"
}

HUMAN_LANGUAGES = [
    "English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam", "Bengali",
    "Telugu-English", "Hindi-English", "Tamil-English", "Kannada-English"
]

# Learning Journey Progression Map (Part A.6)
# Basics -> DSA -> Backend -> APIs -> System Design (HLD) -> Cloud -> Advanced Architecture
LEARNING_JOURNEY_STAGES = [
    {"stage": 1, "name": "Programming Basics", "category": "Other", "keywords": ["Python", "Java", "C", "C++", "JavaScript", "OOP", "Basics"]},
    {"stage": 2, "name": "DSA & Problem Solving", "category": "DSA", "keywords": ["DSA", "Data Structures", "Algorithms", "Coding Interviews"]},
    {"stage": 3, "name": "Backend Engineering", "category": "Java", "keywords": ["Backend", "Spring Boot", "Django", "FastAPI", "Databases", "Node.js", "Express.js"]},
    {"stage": 4, "name": "APIs & Services", "category": "Other", "keywords": ["APIs", "REST", "GraphQL", "Microservices", "PostgreSQL", "Redis"]},
    {"stage": 5, "name": "System Design & HLD", "category": "HLD", "keywords": ["HLD", "System Design", "Distributed Systems", "Load Balancing", "Caching", "Kafka"]},
    {"stage": 6, "name": "Cloud & DevOps", "category": "Cloud", "keywords": ["Cloud", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "DevOps"]},
    {"stage": 7, "name": "Advanced Architecture & AI", "category": "AI", "keywords": ["AI/ML", "Generative AI", "Deep Learning", "High Scale Architecture"]}
]

# Hierarchical parent domain rollups
DOMAIN_ROLLUPS: Dict[str, str] = {
    # Programming Languages
    "Java": "Software Engineering / Backend",
    "Python": "AI / Data Science / Backend",
    "JavaScript": "Web Development / Frontend",
    "TypeScript": "Web Development / Frontend",
    "Go": "Systems / Backend Engineering",
    "Rust": "Systems Programming / High Performance",
    "C++": "Systems / High Performance",
    "C#": "Backend / Enterprise Development",
    "Kotlin": "Mobile / Android Development",
    "Swift": "Mobile / iOS Development",
    
    # Frameworks
    "Spring Boot": "Software Engineering / Backend",
    "Django": "Software Engineering / Backend",
    "FastAPI": "Software Engineering / Backend",
    "React": "Web Development / Frontend",
    "Vue": "Web Development / Frontend",
    "Angular": "Web Development / Frontend",
    "PyTorch": "AI / Machine Learning",
    "TensorFlow": "AI / Machine Learning",
    "Node.js": "Software Engineering / Backend",
    "Express.js": "Software Engineering / Backend",

    # Technologies
    "AWS": "Cloud & Distributed Systems",
    "Azure": "Cloud & Distributed Systems",
    "GCP": "Cloud & Distributed Systems",
    "Docker": "DevOps & Cloud Infrastructure",
    "Kubernetes": "DevOps & Cloud Infrastructure",
    "PostgreSQL": "Databases & Storage",
    "MongoDB": "Databases & Storage",
    "Redis": "Caching & Backend Scaling",
    "Kafka": "Distributed Systems & Streaming",

    # Concepts
    "DSA": "Algorithms & Problem Solving",
    "Data Structures": "Algorithms & Problem Solving",
    "Algorithms": "Algorithms & Problem Solving",
    "OOP": "Software Design Principles",
    "APIs": "Backend & System Integration",
    "REST": "Backend & System Integration",
    "GraphQL": "Backend & System Integration",
    "HLD": "High Level System Design",
    "LLD": "Low Level System Design",
    "System Design": "High Level System Design",
    "Distributed Systems": "Distributed Systems & Cloud",
    "Microservices": "Backend Architecture",
    "Caching": "Backend Performance",
    "Load Balancing": "High Level System Design",

    # Domains
    "AI/ML": "AI / Machine Learning",
    "Generative AI": "AI / Machine Learning",
    "Deep Learning": "AI / Machine Learning",
    "Cybersecurity": "Cybersecurity & Information Security",
    "Cloud": "Cloud & Distributed Systems",
    "Hardware": "Hardware / Developer Gear",
    "Career": "Software Career & Placements"
}


class TaxonomyGraph:
    """Represents the technology knowledge graph and category mapping engine."""

    def __init__(self, rel_csv_path: Optional[str] = None):
        self.relationships: List[Dict] = []
        self.entity_parents: Dict[str, Set[str]] = {}
        self.prerequisites: Dict[str, Set[str]] = {}
        self.related: Dict[str, Set[str]] = {}

        if rel_csv_path and os.path.exists(rel_csv_path):
            self.load_relationships(rel_csv_path)

    def load_relationships(self, csv_path: str):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                src = row.get("source", "").strip()
                rel = row.get("relationship", "").strip()
                tgt = row.get("target", "").strip()
                diff = row.get("difficulty", "Intermediate").strip()
                relevance = float(row.get("career_relevance", 0.8))

                self.relationships.append({
                    "source": src,
                    "relationship": rel,
                    "target": tgt,
                    "difficulty": diff,
                    "career_relevance": relevance
                })

                if rel == "prerequisite_for":
                    self.prerequisites.setdefault(tgt, set()).add(src)
                elif rel == "related_to":
                    self.related.setdefault(src, set()).add(tgt)
                    self.related.setdefault(tgt, set()).add(src)

    def map_to_category_enum(self, topics: str, prog_langs: str, techs: str, frameworks: str, title: str = "") -> str:
        """
        Maps reel metadata to the exact Part A.9 CATEGORY enum:
        ['AI', 'DSA', 'Java', 'HLD', 'Cybersecurity', 'Cloud', 'Hardware', 'Career', 'Other']
        """
        title_lower = title.lower()
        haystack = f"{topics} {prog_langs} {techs} {frameworks} {title}".lower()

        # 1. HLD & System Design (Highest progression priority)
        if any(w in title_lower or w in haystack for w in ["hld", "high level design", "system design", "distributed systems", "load balancer", "load balancing", "microservices", "rate limit", "consistent hashing", "indexes speed up"]):
            return "HLD"
        
        # 2. DSA & Algorithms
        if any(w in title_lower for w in ["dsa", "data structure", "algorithm", "binary search", "leetcode", "trees", "graphs", "sorting"]) or (topics == "DSA" and "explained simply" not in title_lower):
            return "DSA"

        # 3. AI & Machine Learning (Only if genuinely AI focused, not generic title with random domain tag)
        if any(w in title_lower for w in ["vector database", "ml api", "deploy models", "machine learning", "deep learning", "neural network", "generative ai", "llm", "ai news", "ai engineer", "ai tools"]) or ("ai/ml" in haystack and not any(w in title_lower for w in ["explained simply", "developers be like", "moment that broke"])):
            return "AI"

        # 4. Cybersecurity
        if any(w in title_lower or w in haystack for w in ["cybersecurity", "penetration testing", "linux security", "networking security", "kali", "firewall", "vulnerability", "infosec"]):
            return "Cybersecurity"

        # 5. Cloud & DevOps
        if any(w in title_lower for w in ["cloud", "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "devops", "s3", "ec2", "scalable backend api"]):
            return "Cloud"

        # 6. Hardware & Developer Gear
        if any(w in title_lower or w in haystack for w in ["hardware", "gpu", "laptop", "cpu", "macbook", "developer gear", "developer setup", "monitor", "mechanical keyboard"]):
            return "Hardware"

        # 7. Career & Placements
        if any(w in title_lower for w in ["technical interviews", "interview", "resume", "placement", "salary", "promotion", "internship", "career roadmap", "software engineering careers"]):
            return "Career"

        # 8. Java
        if "java" in title_lower or "java" in prog_langs.lower() or "spring boot" in haystack:
            return "Java"

        return "Other"

    def get_parent_domain(self, entity: str) -> str:
        """Rolls an entity up to its broader domain."""
        if entity in DOMAIN_ROLLUPS:
            return DOMAIN_ROLLUPS[entity]
        for key, domain in DOMAIN_ROLLUPS.items():
            if key.lower() == entity.lower():
                return domain
        return "Technology / Engineering"

    def get_prerequisites(self, concept: str) -> List[str]:
        return list(self.prerequisites.get(concept, []))

    def get_related_entities(self, entity: str) -> List[str]:
        return list(self.related.get(entity, []))
