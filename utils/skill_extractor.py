"""
Categorized Skill Extraction Utility
======================================
Extracts technical skills and tools from text using an extensible taxonomy,
alias normalization, and n-gram keyword pattern matching.
Categorizes skills into distinct industry-standard domains.
"""

import re
from typing import Dict, List, Set, Tuple

# Comprehensive Technical Skill Taxonomy organized by category
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", 
        "Ruby", "PHP", "Go", "Rust", "Swift", "Kotlin", "R", "SQL", 
        "Scala", "Dart", "MATLAB", "Bash", "Shell", "HTML", "CSS"
    ],
    "Web Development": [
        "React", "Angular", "Vue.js", "Next.js", "Node.js", "Express.js", 
        "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", "HTML5", 
        "CSS3", "Tailwind CSS", "Bootstrap", "REST APIs", "GraphQL", 
        "WebSockets", "Redux", "Microservices"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Oracle", 
        "Microsoft SQL Server", "Cassandra", "DynamoDB", "Neo4j", 
        "Elasticsearch", "Firebase", "Snowflake", "BigQuery"
    ],
    "Frameworks & Libraries": [
        "PyTorch", "TensorFlow", "Keras", "Scikit-learn", "Pandas", 
        "NumPy", "SciPy", "OpenCV", "Hugging Face", "NLTK", "spaCy", 
        "Streamlit", "LangChain", "LlamaIndex", "jQuery"
    ],
    "Cloud & DevOps": [
        "AWS", "Microsoft Azure", "Google Cloud", "Docker", "Kubernetes", 
        "Jenkins", "CI/CD", "Git", "GitHub Actions", "GitLab CI", 
        "Terraform", "Ansible", "Linux", "Nginx", "Apache"
    ],
    "Data Science & AI/ML": [
        "Machine Learning", "Deep Learning", "Natural Language Processing", 
        "Computer Vision", "Large Language Models", "Generative AI", 
        "Data Analysis", "Data Visualization", "ETL", "Apache Spark", 
        "Power BI", "Tableau", "Time Series Analysis", "Reinforcement Learning"
    ],
    "Developer Tools & Testing": [
        "VS Code", "Postman", "Jira", "Pytest", "JUnit", "Selenium", 
        "Swagger", "Linux", "GitHub", "GitLab", "Bitbucket", "Vim"
    ]
}

# Alias / Synonym mapping to standardize variations to canonical skill names
SKILL_ALIASES: Dict[str, str] = {
    # Languages
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "golang": "Go",
    "cpp": "C++",
    "csharp": "C#",
    "c sharp": "C#",
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "ms sql": "Microsoft SQL Server",
    "mssql": "Microsoft SQL Server",
    
    # Web & Frameworks
    "reactjs": "React",
    "react.js": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "tailwind": "Tailwind CSS",
    
    # Cloud & DevOps
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "k8s": "Kubernetes",
    "github action": "GitHub Actions",
    
    # ML / AI / Data
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "llm": "Large Language Models",
    "llms": "Large Language Models",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "spark": "Apache Spark",
    "bi": "Power BI",
    "powerbi": "Power BI"
}


def _prepare_skill_lookup() -> Dict[str, Tuple[str, str]]:
    """
    Builds a normalized lowercase lookup dictionary mapping:
    normalized_phrase -> (Canonical Name, Category Name)
    """
    lookup: Dict[str, Tuple[str, str]] = {}

    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            norm_canonical = skill.lower()
            lookup[norm_canonical] = (skill, category)

    # Add aliases
    for alias, canonical in SKILL_ALIASES.items():
        norm_alias = alias.lower()
        category_found = "Other Technical Skills"
        for cat, skills in SKILL_TAXONOMY.items():
            if canonical in skills:
                category_found = cat
                break
        lookup[norm_alias] = (canonical, category_found)

    return lookup


# Global pre-compiled lookup dictionary for fast runtime evaluation
LOOKUP_CACHE: Dict[str, Tuple[str, str]] = _prepare_skill_lookup()


def normalize_text_for_skills(text: str) -> str:
    """
    Normalizes text for precision skill keyword search:
    - Lowercases text
    - Strips sentence-terminating punctuation while preserving tech characters (C++, C#, .NET, Vue.js, CI/CD)
    """
    t = " " + text.lower() + " "
    
    # Replace common brackets, parentheses, quotes, commas, semicolons, exclamation with spaces
    t = re.sub(r"[\(\)\[\]\{\}\"\'`,;:!?\\]", " ", t)
    
    # Replace periods that are sentence endings or bullet points (followed by whitespace or end of line)
    t = re.sub(r"\.(?=\s|$)", " ", t)
    
    # Collapse multiple spaces
    t = re.sub(r"\s+", " ", t)
    return t


def extract_skills(text: str) -> dict:
    """
    Extracts categorized technical skills from raw or cleaned text.
    
    Returns:
    {
        "categorized_skills": { "Category": [Skill1, Skill2], ... },
        "all_skills": [Skill1, Skill2, ...],
        "skill_counts": { "Category": count, ... },
        "total_skills_found": int
    }
    """
    result = {
        "categorized_skills": {cat: [] for cat in SKILL_TAXONOMY.keys()},
        "all_skills": [],
        "skill_counts": {cat: 0 for cat in SKILL_TAXONOMY.keys()},
        "total_skills_found": 0
    }

    if not text or not isinstance(text, str):
        return result

    # Normalize text preserving tech tokens
    normalized_text = normalize_text_for_skills(text)

    found_skills_map: Dict[str, str] = {}  # Canonical -> Category

    # Multi-word phrase search first (longer phrases take precedence to avoid partial overlaps)
    sorted_lookup = sorted(LOOKUP_CACHE.items(), key=lambda x: len(x[0].split()), reverse=True)

    for phrase, (canonical, category) in sorted_lookup:
        # Regex boundary check ensuring exact phrase match
        escaped_phrase = re.escape(phrase)
        pattern = r"(?<![\w+#.-])" + escaped_phrase + r"(?![\w+#.-])"
        
        if re.search(pattern, normalized_text):
            found_skills_map[canonical] = category

    # Populate structured result
    for canonical, category in found_skills_map.items():
        if category in result["categorized_skills"]:
            result["categorized_skills"][category].append(canonical)
        else:
            result["categorized_skills"].setdefault("Other Technical Skills", []).append(canonical)

    # Sort skills within each category
    for cat in result["categorized_skills"]:
        result["categorized_skills"][cat].sort()
        result["skill_counts"][cat] = len(result["categorized_skills"][cat])

    # Flat unique skills list
    all_unique = sorted(list(found_skills_map.keys()))
    result["all_skills"] = all_unique
    result["total_skills_found"] = len(all_unique)

    return result
