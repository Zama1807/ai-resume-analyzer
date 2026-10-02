"""
Job Description Analyzer Utility
=================================
Parses job descriptions, extracting target role title, experience and
education requirements, partitioned required vs preferred technical skills,
and critical domain keywords.
"""

import re
from typing import Dict, List, Tuple
from utils.text_cleaner import clean_text, extract_clean_words
from utils.skill_extractor import extract_skills

# Common job title patterns for heuristic detection
ROLE_PATTERNS = [
    r"(?:job\s+title|role|position)\s*[:\-]\s*([a-zA-Z0-9\s\/\+\#\-]+)",
    r"\b(python\s+developer|full[\s\-]stack\s+developer|backend\s+developer|software\s+developer|software\s+engineer|data\s+scientist|data\s+analyst|machine\s+learning\s+engineer|ml\s+engineer|ai\s+engineer|devops\s+engineer|cloud\s+engineer|frontend\s+developer)\b"
]

# Section markers for separating Required vs Preferred qualifications
REQUIRED_MARKERS = [
    r"\b(?:minimum\s+)?requirements?\b",
    r"\bmust\s+have\b",
    r"\bminimum\s+qualifications?\b",
    r"\brequired\s+(?:skills?|qualifications?|experience)\b",
    r"\bwhat\s+(?:you\s+need|you\'ll\s+bring)\b",
    r"\bcore\s+requirements?\b"
]

PREFERRED_MARKERS = [
    r"\bpreferred\s+(?:qualifications?|skills?|experience)\b",
    r"\bnice\s+to\s+have\b",
    r"\bbonus\s+(?:points?|qualifications?|skills?)\b",
    r"\bgood\s+to\s+have\b",
    r"\bdesired\s+(?:skills?|qualifications?)\b",
    r"\bplus(?:es)?\b"
]

# Common English stopwords to ignore in keyword frequency
COMMON_STOPWORDS = {
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", 
    "this", "with", "i", "you", "it", "not", "or", "be", "are", "from", 
    "at", "as", "your", "all", "have", "new", "more", "an", "was", "we", 
    "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", 
    "free", "but", "our", "one", "other", "do", "no", "information", "time", 
    "they", "site", "he", "up", "may", "what", "which", "their", "news", 
    "out", "use", "any", "there", "see", "only", "so", "his", "when", "contact", 
    "here", "business", "who", "web", "also", "now", "help", "get", "pm", "view", 
    "online", "first", "am", "been", "would", "how", "were", "me", "s", "services", 
    "some", "these", "click", "its", "like", "service", "x", "than", "find", 
    "date", "back", "top", "people", "had", "list", "name", "just", "over", 
    "state", "year", "day", "into", "email", "two", "health", "world", "re", 
    "next", "used", "go", "work", "last", "most", "products", "music", "buy", 
    "data", "make", "them", "should", "product", "system", "post", "her", "city", 
    "t", "add", "policy", "number", "such", "please", "available", "copyright", 
    "support", "message", "after", "best", "software", "then", "jan", "good", 
    "well", "where", "info", "rights", "public", "books", "high", "school", 
    "through", "m", "each", "links", "she", "review", "years", "order", "very", 
    "privacy", "book", "items", "company", "read", "group", "need", "many", 
    "user", "said", "de", "does", "set", "under", "general", "research", 
    "university", "january", "mail", "full", "map", "reviews", "program", "life"
}


def extract_role_title(text: str) -> str:
    """
    Detects job role/title from text or headers.
    """
    if not text:
        return "Software Engineering Candidate"

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Check first 3 lines directly for job title keywords
    for line in lines[:3]:
        for pattern in ROLE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) <= 45:
                    return title.title()

    # 2. Check full text for explicit "Job Title:" prefix
    title_match = re.search(r"(?:job\s+title|role|position)\s*[:\-]\s*([^\n\r]+)", text, re.IGNORECASE)
    if title_match:
        cand = title_match.group(1).strip()
        if 3 <= len(cand) <= 50:
            return cand.title()

    # 3. Search for any standard role names anywhere in the text
    for pattern in ROLE_PATTERNS[1:]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

    return "Software Engineering Role"


def extract_experience_requirement(text: str) -> str:
    """
    Extracts years of experience or career level (Entry-Level, Mid, Senior).
    """
    if not text:
        return "Not specified"

    # Regex for year ranges: "3+ years", "2-5 years", "1 to 3 years"
    exp_pattern = r"\b(\d{1,2}(?:\s*(?:-|to)\s*\d{1,2}|\+)?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?)\b"
    matches = re.findall(exp_pattern, text, re.IGNORECASE)
    if matches:
        return matches[0].strip()

    if re.search(r"\b(entry[\s\-]level|freshers?|intern(?:ship)?|new\s+grad(?:uate)?)\b", text, re.IGNORECASE):
        return "Entry-Level / 0-1 Years"
    elif re.search(r"\b(senior|lead|principal|architect)\b", text, re.IGNORECASE):
        return "Senior Level (5+ Years)"
    elif re.search(r"\b(mid[\s\-]level|intermediate)\b", text, re.IGNORECASE):
        return "Mid-Level (2-4 Years)"

    return "Flexible / Open to all experience levels"


def extract_education_requirement(text: str) -> str:
    """
    Identifies academic degree requirements.
    """
    if not text:
        return "Not specified"

    if re.search(r"\b(ph\.?d|doctorate)\b", text, re.IGNORECASE):
        return "Ph.D. in Computer Science or related STEM field"
    elif re.search(r"\b(master\'?s?|m\.?s\.?|m\.?tech)\b", text, re.IGNORECASE):
        return "Master's degree in Computer Science or related field"
    elif re.search(r"\b(bachelor\'?s?|b\.?s\.?|b\.?tech|b\.?e\.?|degree)\b", text, re.IGNORECASE):
        return "Bachelor's degree in Computer Science, Engineering, or relevant experience"

    return "Bachelor's degree or equivalent practical experience"


def partition_skills(text: str, all_skills: List[str]) -> Tuple[List[str], List[str]]:
    """
    Partitions detected skills into Required Skills vs Preferred Skills
    based on section boundary cues.
    """
    req_text = ""
    pref_text = ""
    lines = text.split("\n")

    current_mode = "required"  # default assumption
    req_lines = []
    pref_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for Preferred header
        if any(re.search(pat, stripped, re.IGNORECASE) for pat in PREFERRED_MARKERS):
            current_mode = "preferred"
            continue
        # Check for Required header
        elif any(re.search(pat, stripped, re.IGNORECASE) for pat in REQUIRED_MARKERS):
            current_mode = "required"
            continue

        if current_mode == "preferred":
            pref_lines.append(stripped)
        else:
            req_lines.append(stripped)

    req_text = "\n".join(req_lines)
    pref_text = "\n".join(pref_lines)

    req_skills_dict = extract_skills(req_text)
    pref_skills_dict = extract_skills(pref_text)

    req_skills = set(req_skills_dict["all_skills"])
    pref_skills = set(pref_skills_dict["all_skills"])

    # If preferred skills were also in required, keep them in required
    pref_skills = pref_skills - req_skills

    # Any leftover skills from overall extraction default to required
    remaining = set(all_skills) - req_skills - pref_skills
    req_skills.update(remaining)

    return sorted(list(req_skills)), sorted(list(pref_skills))


def extract_key_terms(text: str, top_n: int = 15) -> List[str]:
    """
    Extracts top technical and operational keywords using frequency analysis.
    """
    words = extract_clean_words(text)
    freq: Dict[str, int] = {}
    for w in words:
        if len(w) >= 3 and w not in COMMON_STOPWORDS and not w.isdigit():
            freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:top_n]]


def analyze_job_description(raw_text: str) -> dict:
    """
    Comprehensive job description analysis function.
    Returns structured insights on role, requirements, skills, and keywords.
    """
    result = {
        "success": False,
        "error_message": "",
        "cleaned_text": "",
        "role_title": "",
        "experience_required": "",
        "education_required": "",
        "all_skills": [],
        "required_skills": [],
        "preferred_skills": [],
        "categorized_skills": {},
        "top_keywords": [],
        "word_count": 0
    }

    if not raw_text or not raw_text.strip():
        result["error_message"] = "Job description text is empty."
        return result

    cleaned = clean_text(raw_text)
    if len(cleaned.split()) < 15:
        result["error_message"] = "Job description is too short (less than 15 words) to perform meaningful NLP analysis."
        return result

    result["cleaned_text"] = cleaned
    result["word_count"] = len(cleaned.split())
    result["role_title"] = extract_role_title(cleaned)
    result["experience_required"] = extract_experience_requirement(cleaned)
    result["education_required"] = extract_education_requirement(cleaned)

    # Extract all skills using the taxonomy engine
    skills_data = extract_skills(cleaned)
    result["all_skills"] = skills_data["all_skills"]
    result["categorized_skills"] = skills_data["categorized_skills"]

    # Partition into Required vs Preferred
    req_skills, pref_skills = partition_skills(cleaned, result["all_skills"])
    result["required_skills"] = req_skills
    result["preferred_skills"] = pref_skills

    # Extract domain keywords
    result["top_keywords"] = extract_key_terms(cleaned)

    result["success"] = True
    return result
