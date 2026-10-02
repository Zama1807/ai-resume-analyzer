"""
Unit Tests for Recommendations and Role Matching
"""

import pytest
from utils.recommendations import recommend_roles, generate_improvement_suggestions

def test_recommend_roles_ranks_python_backend_high():
    skills = ["Python", "FastAPI", "SQL", "Git", "REST APIs", "PostgreSQL", "Docker"]
    roles = recommend_roles(skills)
    
    assert len(roles) > 0
    top_role = roles[0]["role"]
    # With these skills, Python Developer or Backend Developer should top the ranking
    assert top_role in ["Python Developer", "Backend Developer"]
    assert roles[0]["match_score"] >= 70.0

def test_recommend_roles_ranks_ml_high_when_ml_skills_present():
    skills = ["Python", "Machine Learning", "PyTorch", "TensorFlow", "Scikit-learn", "Pandas", "NLP"]
    roles = recommend_roles(skills)
    
    top_role = roles[0]["role"]
    assert top_role == "Machine Learning / AI Intern"
    assert roles[0]["match_score"] >= 85.0

def test_generate_improvement_suggestions():
    mock_resume = {
        "cleaned_text": "Short resume text without numbers",
        "sections": {"skills": "Python", "experience": "Coder"}
    }
    mock_match = {
        "missing_required_skills": ["Docker", "Kubernetes"],
        "missing_preferred_skills": ["AWS"],
        "missing_keywords": ["microservices", "agile"]
    }
    suggestions = generate_improvement_suggestions(mock_resume, mock_match)
    
    assert len(suggestions["skills_to_learn"]) >= 1
    assert "Docker" in suggestions["skills_to_learn"][0]
    assert len(suggestions["keyword_improvements"]) >= 1
    assert "microservices" in suggestions["keyword_improvements"][0]
