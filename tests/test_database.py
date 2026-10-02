"""
Unit Tests for SQLite Database Operations
"""

import pytest
import os
from utils.database import init_db, save_analysis, get_all_analyses, get_analysis_by_id, delete_analysis

TEST_DB = os.path.join("data", "test_database.db")

@pytest.fixture(autouse=True)
def cleanup():
    # Cleanup test DB before and after
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_crud_operations():
    init_db(TEST_DB)
    assert os.path.exists(TEST_DB)

    # 1. Insert Record
    rec_id = save_analysis(
        candidate_name="Alex Johnson",
        candidate_email="alex@example.com",
        job_role="Python Developer",
        overall_score=85.5,
        tfidf_score=72.0,
        matched_skills=["Python", "FastAPI", "SQL"],
        missing_skills=["Docker"],
        explanation="Weighted test explanation",
        db_path=TEST_DB
    )
    assert rec_id == 1

    # 2. Retrieve All
    all_recs = get_all_analyses(TEST_DB)
    assert len(all_recs) == 1
    assert all_recs[0]["candidate_name"] == "Alex Johnson"
    assert all_recs[0]["overall_score"] == 85.5
    assert "FastAPI" in all_recs[0]["matched_skills"]

    # 3. Retrieve by ID
    single = get_analysis_by_id(rec_id, TEST_DB)
    assert single is not None
    assert single["job_role"] == "Python Developer"

    # 4. Delete Record
    success = delete_analysis(rec_id, TEST_DB)
    assert success is True
    assert len(get_all_analyses(TEST_DB)) == 0
