"""
Unit Tests for Resume vs Job Matching Engine
"""

import pytest
from utils.matcher import compute_tfidf_similarity, calculate_match

def test_tfidf_identical_and_unrelated_texts():
    t1 = "Python developer with experience in Django, FastAPI, SQL, and Docker."
    score_identical = compute_tfidf_similarity(t1, t1)
    assert score_identical >= 98.0  # Cosine similarity of identical text is ~100%

    t2 = "Experienced registered pediatric nurse working in intensive emergency care."
    score_unrelated = compute_tfidf_similarity(t1, t2)
    assert score_unrelated <= 15.0

def test_calculate_match_structure_and_formula():
    resume_mock = {
        "cleaned_text": "Experienced Python software developer working with FastAPI, PostgreSQL, and Git.",
        "skills_analysis": {
            "all_skills": ["Python", "FastAPI", "PostgreSQL", "Git", "Redis"]
        }
    }
    
    job_mock = {
        "cleaned_text": "Looking for a Python Engineer skilled in FastAPI, PostgreSQL, and AWS.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "preferred_skills": ["AWS", "Redis"],
        "all_skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Redis"],
        "top_keywords": ["python", "engineer", "software", "cloud"]
    }
    
    result = calculate_match(resume_mock, job_mock)
    
    # 3 required skills in resume -> 100% required skills score
    assert result["required_skills_score"] == 100.0
    assert "Python" in result["matched_required_skills"]
    assert "FastAPI" in result["matched_required_skills"]
    assert "PostgreSQL" in result["matched_required_skills"]
    assert len(result["missing_required_skills"]) == 0
    
    # Preferred skills
    assert "Redis" in result["matched_preferred_skills"]
    assert "AWS" in result["missing_preferred_skills"]
    
    # Overall score must be > 60%
    assert result["overall_match_score"] >= 60.0
    assert "mathematically derived" in result["explanation"]
