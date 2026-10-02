"""
Unit Tests for ATS-Oriented Resume Auditor
"""

import pytest
from utils.ats_analyzer import analyze_ats_compliance

def test_ats_compliance_with_complete_resume():
    mock_resume = {
        "cleaned_text": "Alex Johnson. Developed APIs using Python, optimized database queries, engineered web apps.",
        "sections": {
            "skills": "Python, SQL, Docker",
            "experience": "Software Developer at Acme. Developed services.",
            "education": "B.S. in Computer Science",
            "projects": "Personal project using Python."
        },
        "contact_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
            "phone": "+1 555-1234"
        },
        "page_count": 1,
        "word_count": 250,
        "skills_analysis": {"all_skills": ["Python", "SQL", "Docker"]}
    }

    mock_job = {
        "success": True,
        "required_skills": ["Python", "SQL"],
        "top_keywords": ["python", "apis", "database"]
    }

    result = analyze_ats_compliance(mock_resume, mock_job)
    assert result["ats_score"] >= 80.0
    assert result["metrics"]["completeness_score"] == 100.0
    assert result["section_audit"]["skills"]["status"] == "PASS"
    assert result["section_audit"]["education"]["status"] == "PASS"
    assert "Notice:" in result["disclaimer"]

def test_ats_missing_critical_sections():
    incomplete_resume = {
        "cleaned_text": "Random text without sections",
        "sections": {},
        "contact_info": {"name": "Test"},
        "page_count": 4,
        "word_count": 50,
        "skills_analysis": {"all_skills": []}
    }

    result = analyze_ats_compliance(incomplete_resume)
    assert result["ats_score"] < 50.0
    assert result["metrics"]["completeness_score"] == 0.0
    assert any(item["status"] in ["FAIL", "WARNING"] for item in result["formatting_audit"])
