"""
Unit Tests for Categorized Skill Extractor
"""

import pytest
from utils.skill_extractor import extract_skills

def test_extract_single_and_multiword_skills():
    text = "Proficient in Python, C++, React, and Machine Learning with PostgreSQL and Docker."
    result = extract_skills(text)
    
    assert "Python" in result["all_skills"]
    assert "C++" in result["all_skills"]
    assert "React" in result["all_skills"]
    assert "Machine Learning" in result["all_skills"]
    assert "PostgreSQL" in result["all_skills"]
    assert "Docker" in result["all_skills"]

def test_skill_aliases_normalization():
    text = "Built services with postgres, k8s, reactjs, and sklearn."
    result = extract_skills(text)
    
    assert "PostgreSQL" in result["all_skills"]
    assert "Kubernetes" in result["all_skills"]
    assert "React" in result["all_skills"]
    assert "Scikit-learn" in result["all_skills"]

def test_skill_categorization_integrity():
    text = "Experience with Java, Django, MongoDB, AWS, and Pytest."
    result = extract_skills(text)
    
    assert "Java" in result["categorized_skills"]["Programming Languages"]
    assert "Django" in result["categorized_skills"]["Web Development"]
    assert "MongoDB" in result["categorized_skills"]["Databases"]
    assert "AWS" in result["categorized_skills"]["Cloud & DevOps"]
    assert "Pytest" in result["categorized_skills"]["Developer Tools & Testing"]

def test_empty_and_noise_text():
    empty_res = extract_skills("")
    assert empty_res["total_skills_found"] == 0
    assert empty_res["all_skills"] == []

    noise_res = extract_skills("The quick brown fox jumps over the lazy dog.")
    assert noise_res["total_skills_found"] == 0
