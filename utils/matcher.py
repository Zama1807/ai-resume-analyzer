"""
Resume vs Job Matching Engine
==============================
Calculates mathematical similarity between candidate resumes and job descriptions
using Scikit-learn TF-IDF Vectorization, Cosine Similarity, and Set-Theoretic
Skill & Keyword Overlap analysis.
No hardcoded scores or fake AI percentages.
"""

from typing import Dict, List, Set, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_cleaner import clean_text

def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """
    Computes mathematical Cosine Similarity between Resume and Job text
    using Scikit-Learn TF-IDF vectorization with unigrams and bigrams.
    Returns a score between 0.0 and 100.0.
    """
    if not resume_text.strip() or not job_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity_matrix[0][0]) * 100.0
        return round(max(0.0, min(100.0, score)), 2)
    except Exception:
        return 0.0


def calculate_match(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes comprehensive match analytics between resume and job description:
    1. Overall Weighted Match Percentage
    2. TF-IDF Cosine Similarity
    3. Matched & Missing Required Skills
    4. Matched & Missing Preferred Skills
    5. Domain Keyword Overlap
    6. Mathematical Score Calculation Explanation
    """
    resume_text = resume_data.get("cleaned_text", "")
    job_text = job_data.get("cleaned_text", "")
    
    # 1. Candidate Skills
    candidate_skills = set(resume_data.get("skills_analysis", {}).get("all_skills", []))
    
    # 2. Job Skills
    job_required = set(job_data.get("required_skills", []))
    job_preferred = set(job_data.get("preferred_skills", []))
    all_job_skills = set(job_data.get("all_skills", []))

    # Fallback if partitioning returned empty
    if not job_required and all_job_skills:
        job_required = all_job_skills

    # 3. Exact Skill Intersections
    matched_required = sorted(list(candidate_skills.intersection(job_required)))
    missing_required = sorted(list(job_required.difference(candidate_skills)))
    
    matched_preferred = sorted(list(candidate_skills.intersection(job_preferred)))
    missing_preferred = sorted(list(job_preferred.difference(candidate_skills)))

    all_matched_skills = sorted(list(candidate_skills.intersection(all_job_skills)))
    all_missing_skills = sorted(list(all_job_skills.difference(candidate_skills)))

    # Additional skills the candidate has that weren't explicitly in the job description
    bonus_candidate_skills = sorted(list(candidate_skills.difference(all_job_skills)))

    # 4. Keyword Matches
    job_keywords = job_data.get("top_keywords", [])
    resume_lower = resume_text.lower()
    
    matched_keywords = [kw for kw in job_keywords if kw.lower() in resume_lower]
    missing_keywords = [kw for kw in job_keywords if kw.lower() not in resume_lower]

    # 5. Component Scoring
    # A. TF-IDF Cosine Score (0 - 100)
    tfidf_score = compute_tfidf_similarity(resume_text, job_text)

    # B. Required Skills Score (0 - 100)
    if job_required:
        req_score = (len(matched_required) / len(job_required)) * 100.0
    else:
        req_score = 100.0 if not all_job_skills else 0.0

    # C. Preferred Skills Score (0 - 100)
    if job_preferred:
        pref_score = (len(matched_preferred) / len(job_preferred)) * 100.0
    else:
        pref_score = None  # No preferred skills specified

    # D. Keyword Coverage Score (0 - 100)
    if job_keywords:
        kw_score = (len(matched_keywords) / len(job_keywords)) * 100.0
    else:
        kw_score = 0.0

    # 6. Overall Match Score Calculation
    # Industry formula:
    # If preferred skills exist: 50% Required Skills + 30% TF-IDF Cosine Similarity + 20% Preferred Skills
    # If no preferred skills: 65% Required Skills + 35% TF-IDF Cosine Similarity
    if pref_score is not None:
        overall_score = (0.50 * req_score) + (0.30 * tfidf_score) + (0.20 * pref_score)
        explanation = (
            f"Overall Match Score of {overall_score:.1f}% is mathematically derived from: "
            f"Core Required Skills ({req_score:.1f}% @ 50% weight) + "
            f"TF-IDF Semantic Similarity ({tfidf_score:.1f}% @ 30% weight) + "
            f"Preferred Qualifications ({pref_score:.1f}% @ 20% weight)."
        )
    elif job_required:
        overall_score = (0.65 * req_score) + (0.35 * tfidf_score)
        explanation = (
            f"Overall Match Score of {overall_score:.1f}% is mathematically derived from: "
            f"Core Required Skills ({req_score:.1f}% @ 65% weight) + "
            f"TF-IDF Semantic Similarity ({tfidf_score:.1f}% @ 35% weight)."
        )
    else:
        overall_score = tfidf_score
        explanation = f"Overall Match Score of {overall_score:.1f}% is based on TF-IDF Semantic Content Similarity."

    overall_score = round(max(0.0, min(100.0, overall_score)), 1)

    return {
        "overall_match_score": overall_score,
        "tfidf_score": round(tfidf_score, 1),
        "required_skills_score": round(req_score, 1),
        "preferred_skills_score": round(pref_score, 1) if pref_score is not None else 0.0,
        "keyword_coverage_score": round(kw_score, 1),
        
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        
        "all_matched_skills": all_matched_skills,
        "all_missing_skills": all_missing_skills,
        "bonus_candidate_skills": bonus_candidate_skills,
        
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        
        "explanation": explanation
    }
