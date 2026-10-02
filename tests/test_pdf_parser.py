"""
Unit Tests for PDF Parser and Text Cleaning
"""

import pytest
import os
from utils.text_cleaner import clean_text, extract_clean_words
from utils.pdf_parser import parse_pdf, extract_contact_info, extract_sections

def test_clean_text_removes_bullets_and_whitespace():
    raw = "  • Python \n\n\n  • FastAPI \t\t and SQL   "
    cleaned = clean_text(raw)
    assert "Python" in cleaned
    assert "FastAPI" in cleaned
    assert "•" not in cleaned

def test_extract_clean_words():
    text = "Python, Machine-Learning, & C++!"
    words = extract_clean_words(text)
    assert "python" in words
    assert "c++" in words

def test_extract_contact_info_regex():
    sample = (
        "Sarah Connor\n"
        "Email: sarah.connor@cyberdyne.io\n"
        "Phone: +1 (555) 987-6543\n"
        "GitHub: github.com/sarahconnor\n"
    )
    contact = extract_contact_info(sample)
    assert contact["name"] == "Sarah Connor"
    assert contact["email"] == "sarah.connor@cyberdyne.io"
    assert "555" in contact["phone"]
    assert "sarahconnor" in contact["github"]

def test_parse_pdf_sample_file():
    sample_path = os.path.join("assets", "sample_resume.pdf")
    if os.path.exists(sample_path):
        res = parse_pdf(sample_path)
        assert res["success"] is True
        assert res["page_count"] >= 1
        assert res["contact_info"]["name"] == "Alex Johnson"
        assert "skills" in res["detected_sections_list"]
