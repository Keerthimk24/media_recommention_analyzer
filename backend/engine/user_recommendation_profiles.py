"""
backend/engine/user_recommendation_profiles.py

Exact curated recommendation sequences for all 89 users (U001 to U089).
Verbatim titles matching the user's exact specification table.
"""

from typing import Dict, List, Any, Optional

# (user_id, item1, item2, item3, item4, item5)
RAW_SPEC_TABLE = [
    # U001–U020
    ("U001", "REST vs GraphQL", "Scalable Backend API", "Database Indexes", "Consistent Hashing", "System Design URL Shortener"),
    ("U002", "Vector Databases", "ML Model Deployment", "RAG Architecture", "AI Evaluation", "Python ML Pipeline"),
    ("U003", "DSA Patterns", "Algorithms Explained", "Coding Interviews", "Java Interview", "Placement Prep"),
    ("U004", "Cybersecurity News", "Web Security", "Network Security", "Linux Security", "Cloud Security"),
    ("U005", "TypeScript", "React Architecture", "Next.js", "JavaScript", "REST API Integration"),
    ("U006", "Cloud Architecture", "Scalable Backend API", "Load Balancers", "Distributed Systems", "Kubernetes"),
    ("U007", "RAG Applications", "Vector Databases", "LLM Agents", "AI Evaluation", "Prompt Engineering"),
    ("U008", "GPU Architecture", "Hardware Launches", "AI Hardware", "CPU vs GPU", "CUDA"),
    ("U009", "Advanced SQL", "Database Indexes", "Data Analytics", "Python Data Processing", "Data Pipelines"),
    ("U010", "Spring Boot APIs", "REST vs GraphQL", "Database Design", "Microservices", "System Design"),
    ("U011", "Python ML", "Model Deployment", "RAG", "ML Pipelines", "MLOps"),
    ("U012", "Java DSA", "Coding Interviews", "Java Collections", "Algorithms", "Placement Prep"),
    ("U013", "Web Security", "Network Security", "Linux Security", "Cybersecurity News", "Cloud Security"),
    ("U014", "React", "TypeScript", "Frontend Architecture", "Next.js", "API Integration"),
    ("U015", "AI Hardware", "GPU Computing", "CUDA", "ML Deployment", "Python AI"),
    ("U016", "Spring Boot on AWS", "Docker", "AWS Architecture", "Kubernetes", "CI/CD"),
    ("U017", "Graph Algorithms", "Dynamic Programming", "C++ STL", "Competitive Programming", "Advanced DSA"),
    ("U018", "Advanced SQL", "Data Modeling", "Power BI", "ETL", "Database Optimization"),
    ("U019", "Cloud Security", "IAM", "Linux Security", "AWS Security", "Network Defense"),
    ("U020", "GPU Architecture", "AI Hardware", "CUDA", "Gaming Hardware", "CPU vs GPU"),

    # U021–U040
    ("U021", "Django REST API", "Python Backend", "PostgreSQL", "Authentication", "Docker"),
    ("U022", "Node.js APIs", "React + Node", "TypeScript", "MongoDB", "Full-Stack Architecture"),
    ("U023", "Microservices Architecture", "Kafka", "API Gateway", "Spring Cloud", "Distributed Systems"),
    ("U024", "Pandas Advanced", "Feature Engineering", "Statistics for ML", "Data Cleaning", "ML Pipeline"),
    ("U025", "RAG Architecture", "LLM Agents", "Vector Databases", "Prompt Evaluation", "AI Applications"),
    ("U026", "Operating Systems", "Memory Management", "C Pointers", "Processes & Threads", "System Programming"),
    ("U027", "Azure Architecture", "Azure DevOps", "Cloud Containers", "CI/CD", "Infrastructure as Code"),
    ("U028", "OWASP Top 10", "SQL Injection", "XSS", "API Security", "Secure Coding"),
    ("U029", "NLP Pipeline", "Transformers", "Text Embeddings", "RAG", "NLP Projects"),
    ("U030", "SQL Optimization", "Database Indexing", "Java Database Apps", "Transactions", "Database Design"),
    ("U031", "Kotlin Android", "Jetpack Compose", "Android APIs", "App Architecture", "Firebase"),
    ("U032", "SwiftUI", "iOS Architecture", "Swift", "Mobile APIs", "App Deployment"),
    ("U033", "FastAPI Production", "Docker Deployment", "REST APIs", "PostgreSQL", "Cloud Deployment"),
    ("U034", "Hibernate", "JPA", "SQL Optimization", "Spring Data", "Database Design"),
    ("U035", "Next.js", "React Architecture", "Tailwind", "Frontend Performance", "API Integration"),
    ("U036", "CNN Architecture", "OpenCV", "Image Classification", "Transfer Learning", "Vision Deployment"),
    ("U037", "Model Evaluation", "Feature Engineering", "Cross Validation", "ML Pipelines", "Deployment"),
    ("U038", "PyTorch", "CNNs", "Transformers", "GPU Training", "Model Optimization"),
    ("U039", "Array Patterns", "String Algorithms", "HashMaps", "Two Pointers", "Coding Interviews"),
    ("U040", "Python DSA", "Recursion", "Trees", "Graphs", "Dynamic Programming"),

    # U041–U060
    ("U041", "AWS Backend Architecture", "Load Balancing", "EC2 + RDS", "API Scaling", "System Design"),
    ("U042", "Vertex AI", "ML Deployment", "GCP Architecture", "Docker", "MLOps"),
    ("U043", "Kubernetes", "Docker Networking", "CI/CD", "Helm", "Container Security"),
    ("U044", "Jenkins Pipeline", "Git Workflows", "Docker CI", "DevOps Architecture", "Deployment Automation"),
    ("U045", "PostgreSQL Optimization", "Indexes", "Query Planning", "Transactions", "Database Architecture"),
    ("U046", "MongoDB Design", "Node.js APIs", "NoSQL Modeling", "REST APIs", "Backend Scaling"),
    ("U047", "Redis Caching", "Database Performance", "API Optimization", "Distributed Cache", "Backend Scaling"),
    ("U048", "Kafka Architecture", "Event-Driven Systems", "Microservices", "Message Queues", "Distributed Systems"),
    ("U049", "URL Shortener HLD", "Rate Limiter", "Load Balancing", "Consistent Hashing", "Distributed Cache"),
    ("U050", "SOLID Principles", "Design Patterns", "Java LLD", "Object Modeling", "LLD Interview"),
    ("U051", "Java DSA", "Java Collections", "Coding Patterns", "Interview Questions", "System Design"),
    ("U052", "Python AI", "ML Fundamentals", "RAG", "Model Deployment", "AI Career"),
    ("U053", "React", "JavaScript", "TypeScript", "Next.js", "Frontend APIs"),
    ("U054", "AWS Basics", "Cloud Architecture", "IAM", "AWS Networking", "Cloud Security"),
    ("U055", "Cybersecurity Basics", "Linux", "Web Security", "Networking", "Ethical Hacking"),
    ("U056", "PC Components", "GPU Comparison", "CPU Architecture", "Storage", "PC Build"),
    ("U057", "Game Programming", "Java DSA", "Game Engines", "Graphics", "C++ Games"),
    ("U058", "Python Robotics", "Computer Vision", "ROS", "Sensors", "Robot AI"),
    ("U059", "IoT Architecture", "Arduino C++", "Sensors", "MQTT", "IoT Cloud"),
    ("U060", "Embedded C", "Microcontrollers", "RTOS", "Embedded Linux", "IoT Systems"),

    # U061–U089
    ("U061", "SQL Analytics", "Power BI", "Data Cleaning", "Dashboard Design", "Analytics Career"),
    ("U062", "Tableau", "SQL", "Data Modeling", "BI Architecture", "Analytics Projects"),
    ("U063", "ML for Finance", "Python Analytics", "Fraud Detection", "Time Series", "FinTech AI"),
    ("U064", "Healthcare AI", "Medical Imaging", "ML Pipelines", "AI Ethics", "Model Deployment"),
    ("U065", "Hindi NLP", "Transformers", "Text Classification", "Embeddings", "RAG"),
    ("U066", "Telugu RAG", "LLM Applications", "Vector Databases", "AI Agents", "Prompt Evaluation"),
    ("U067", "Cloud Security", "IAM", "Zero Trust", "Network Security", "AWS Security"),
    ("U068", "Kubernetes on AWS", "CI/CD", "Docker", "Cloud Architecture", "Monitoring"),
    ("U069", "Rust Ownership", "Memory Safety", "Rust Backend", "Systems Programming", "Rust vs C++"),
    ("U070", "Go REST APIs", "Go Concurrency", "Microservices", "Docker", "Cloud Deployment"),
    ("U071", "CUDA Programming", "GPU Computing", "C++ AI", "Parallel Computing", "AI Hardware"),
    ("U072", "Laravel APIs", "PHP Backend", "MySQL", "Authentication", "Web Deployment"),
    ("U073", "Rails APIs", "Ruby", "MVC Architecture", "PostgreSQL", "Deployment"),
    ("U074", "Flutter", "Dart", "Firebase", "Mobile Architecture", "API Integration"),
    ("U075", "PostgreSQL Indexes", "Query Optimization", "REST + SQL", "Database Design", "Backend Scaling"),
    ("U076", "TCP/IP", "DNS", "Linux Networking", "Cloud Networking", "Load Balancing"),
    ("U077", "Graph Algorithms", "Dynamic Programming", "Trees", "Greedy Algorithms", "Python DSA"),
    ("U078", "Spring Microservices", "HLD", "API Gateway", "Event-Driven Architecture", "System Design"),
    ("U079", "ML Deployment", "Docker ML", "Kubernetes ML", "Model Monitoring", "MLOps Architecture"),
    ("U080", "Python Security", "Web Vulnerabilities", "Pen Testing", "API Security", "Secure Python"),
    ("U081", "AI Robotics", "Computer Vision", "GPU Computing", "Sensors", "Edge AI"),
    ("U082", "AI Web Apps", "React + AI", "LLM APIs", "Next.js", "AI UI Design"),
    ("U083", "Java Cloud Career", "Backend Interview", "AWS Interview", "System Design", "Resume Tech Stack"),
    ("U084", "ML Engineer Roadmap", "Model Deployment", "MLOps", "ML Interview", "AI Projects"),
    ("U085", "C++ DSA", "Competitive Programming", "Graphs", "Dynamic Programming", "Coding Interviews"),
    ("U086", "Python Projects", "Python Automation", "Pandas", "FastAPI", "Python Career"),
    ("U087", "Java Cloud Deployment", "Spring Boot", "AWS", "Docker", "Backend Architecture"),
    ("U088", "AI Security", "Cloud Security", "LLM Security", "Zero Trust", "Secure AI Systems"),
    ("U089", "AI Engineering Roadmap", "Python ML", "DSA for AI Engineers", "Model Deployment", "AI System Design")
]

def _infer_category(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["rest", "graphql", "api", "apis", "gateway", "integration"]):
        return "APIs"
    if any(w in t for w in ["backend", "spring boot", "django", "laravel", "rails", "fastapi", "node", "php", "ruby"]):
        return "Backend"
    if any(w in t for w in ["hld", "system design", "index", "indexes", "indexing", "consistent hashing", "load balancing", "load balancers", "url shortener", "distributed systems", "database", "sql", "postgresql", "mongodb", "redis", "kafka", "query", "nosql", "sharding", "rate limiter", "transactions", "microservices"]):
        return "HLD"
    if any(w in t for w in ["cloud", "docker", "kubernetes", "aws", "azure", "devops", "gcp", "terraform", "jenkins", "helm", "monitoring", "ci/cd", "deployment"]):
        return "Cloud"
    if any(w in t for w in ["dsa", "algorithm", "algorithms", "binary", "tree", "trees", "sorting", "leetcode", "graph", "graphs", "dp", "dynamic programming", "bit manipulation", "pointers", "hashmaps", "arrays"]):
        return "DSA"
    if any(w in t for w in ["ai", "python", "vector", "ml", "neural", "vision", "nlp", "genai", "llm", "rag", "pytorch", "tensorflow", "chatbots", "models", "transformers", "embeddings"]):
        return "AI"
    if any(w in t for w in ["java", "spring", "hibernate", "jpa"]):
        return "Java"
    if any(w in t for w in ["security", "cybersecurity", "linux", "hacking", "vulnerability", "vulnerabilities", "owasp", "zero trust", "iam", "xss", "injection"]):
        return "Cybersecurity"
    if any(w in t for w in ["hardware", "launch", "launches", "gpu", "pc", "laptop", "gaming", "silicon", "cuda", "embedded", "robotics", "iot", "arduino", "rtos", "sensors", "cpu"]):
        return "Hardware"
    if any(w in t for w in ["career", "placement", "interview", "interviews", "resume", "roadmap", "roadmaps", "salary", "prep"]):
        return "Career"
    if any(w in t for w in ["react", "javascript", "typescript", "frontend", "svelte", "vue", "next.js", "tailwind", "css", "html", "flutter", "swift", "swiftui", "kotlin", "android", "ios", "ui", "ux"]):
        return "Basics"
    return "Other"

USER_RECOMMENDATION_TABLE: Dict[str, Dict[str, Any]] = {}

for uid, r1, r2, r3, r4, r5 in RAW_SPEC_TABLE:
    num_part = uid[1:].lstrip("0") or "0"
    num = int(num_part)
    key_short = f"U{num:03d}"
    key_long = f"U{num:06d}"

    p_title = r1
    p_cat = _infer_category(p_title)
    
    alts = []
    for i, atitle in enumerate([r2, r3, r4, r5]):
        acat = _infer_category(atitle)
        adiff = "Beginner" if i == 0 else ("Advanced" if i == 3 else "Intermediate")
        alts.append({
            "title": atitle,
            "category": acat,
            "difficulty": adiff,
            "summary": f"Learn {atitle} in under a minute"
        })

    profile = {
        "user_id": uid,
        "history_interest": p_cat,
        "current_session": p_cat,
        "category": p_cat,
        "interest_detected": f"{p_cat} / {r1}",
        "primary": {
            "title": p_title,
            "category": p_cat,
            "difficulty": "Intermediate",
            "summary": f"Learn {p_title} in under a minute"
        },
        "alternatives": alts
    }

    USER_RECOMMENDATION_TABLE[uid] = profile
    USER_RECOMMENDATION_TABLE[key_short] = profile
    USER_RECOMMENDATION_TABLE[key_long] = profile


def get_user_curated_recommendation(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the exact curated 5-reel recommendation profile for any user ID."""
    if not user_id:
        return None
    if user_id in USER_RECOMMENDATION_TABLE:
        return USER_RECOMMENDATION_TABLE[user_id]
    
    # Try normalized formats: U000001 -> U001, U1 -> U001, etc.
    if user_id.startswith("U"):
        try:
            num = int(user_id[1:])
            key3 = f"U{num:03d}"
            key6 = f"U{num:06d}"
            if key3 in USER_RECOMMENDATION_TABLE:
                return USER_RECOMMENDATION_TABLE[key3]
            if key6 in USER_RECOMMENDATION_TABLE:
                return USER_RECOMMENDATION_TABLE[key6]
        except ValueError:
            pass
    return None
