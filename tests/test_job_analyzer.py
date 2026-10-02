"""
Unit Tests for Job Description Analyzer
"""

import pytest
from utils.job_analyzer import analyze_job_description

SAMPLE_JD = """
Job Title: Python Full Stack Developer
Company: Innovatech Labs
Location: Remote

About the Role:
We are seeking an ambitious Software Developer to build high-performance web APIs and cloud microservices.

Minimum Requirements:
- 1-3 years of experience in Python software development.
- Strong proficiency in FastAPI, Django, and SQL.
- Hands-on experience with PostgreSQL and Git.
- Bachelor's degree in Computer Science or equivalent.

Preferred Qualifications:
- Experience with Docker, Redis, and React.
- Familiarity with AWS cloud deployment and CI/CD pipelines.
"""

def test_empty_and_short_job_description():
    res_empty = analyze_job_description("")
    assert res_empty["success"] is False
    assert "empty" in res_empty["error_message"].lower()

    res_short = analyze_job_description("Hiring python coder now.")
    assert res_short["success"] is False
    assert "too short" in res_short["error_message"].lower()

def test_job_description_parsing():
    result = analyze_job_description(SAMPLE_JD)
    assert result["success"] is True
    assert "Python" in result["role_title"]
    assert "1-3 years" in result["experience_required"]
    assert "Bachelor" in result["education_required"]
    
    # Required skills verification
    assert "Python" in result["required_skills"]
    assert "FastAPI" in result["required_skills"]
    assert "PostgreSQL" in result["required_skills"]
    
    # Preferred skills verification
    assert "Docker" in result["preferred_skills"] or "Docker" in result["all_skills"]
    assert "Redis" in result["preferred_skills"] or "Redis" in result["all_skills"]
    assert "React" in result["preferred_skills"] or "React" in result["all_skills"]

def test_top_keywords_extraction():
    result = analyze_job_description(SAMPLE_JD)
    assert len(result["top_keywords"]) > 0
    # Common tech tokens should be present
    lower_kws = [k.lower() for k in result["top_keywords"]]
    assert any(k in lower_kws for k in ["python", "developer", "experience", "apis", "cloud", "microservices"])
