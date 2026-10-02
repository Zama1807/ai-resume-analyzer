"""
SQLite History & Persistence Utility
=====================================
Stores analysis session records safely in a local SQLite database using
parameterized SQL queries (preventing SQL injection).
Provides CRUD functionality for audit history tracking.
Ensures explicit connection closure for safe execution across all platforms.
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join("data", "database.db")

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Establishes connection to the SQLite database and ensures the parent directory exists.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes the database schema if tables do not exist.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            candidate_name TEXT NOT NULL,
            candidate_email TEXT,
            job_role TEXT NOT NULL,
            overall_score REAL NOT NULL,
            tfidf_score REAL NOT NULL,
            matched_skills_count INTEGER NOT NULL,
            missing_skills_count INTEGER NOT NULL,
            matched_skills_json TEXT NOT NULL,
            missing_skills_json TEXT NOT NULL,
            explanation TEXT
        );
        """)
        conn.commit()
    finally:
        conn.close()


def save_analysis(
    candidate_name: str,
    candidate_email: str,
    job_role: str,
    overall_score: float,
    tfidf_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    explanation: str,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Inserts a completed analysis record using parameterized SQL.
    Returns the newly generated record ID.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis_history (
                candidate_name,
                candidate_email,
                job_role,
                overall_score,
                tfidf_score,
                matched_skills_count,
                missing_skills_count,
                matched_skills_json,
                missing_skills_json,
                explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_name or "Anonymous Candidate",
            candidate_email or "Not Provided",
            job_role or "Software Engineering Candidate",
            float(overall_score),
            float(tfidf_score),
            len(matched_skills),
            len(missing_skills),
            json.dumps(matched_skills),
            json.dumps(missing_skills),
            explanation
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_analyses(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves all past analyses ordered by creation date descending.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, 
                created_at, 
                candidate_name, 
                candidate_email, 
                job_role, 
                overall_score, 
                tfidf_score, 
                matched_skills_count, 
                missing_skills_count,
                matched_skills_json,
                missing_skills_json,
                explanation
            FROM analysis_history
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "created_at": r["created_at"],
                "candidate_name": r["candidate_name"],
                "candidate_email": r["candidate_email"],
                "job_role": r["job_role"],
                "overall_score": r["overall_score"],
                "tfidf_score": r["tfidf_score"],
                "matched_skills_count": r["matched_skills_count"],
                "missing_skills_count": r["missing_skills_count"],
                "matched_skills": json.loads(r["matched_skills_json"]),
                "missing_skills": json.loads(r["missing_skills_json"]),
                "explanation": r["explanation"]
            })
        return results
    finally:
        conn.close()


def get_analysis_by_id(analysis_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single historical record by primary key ID.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis_history WHERE id = ?
        """, (analysis_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "candidate_name": row["candidate_name"],
            "candidate_email": row["candidate_email"],
            "job_role": row["job_role"],
            "overall_score": row["overall_score"],
            "tfidf_score": row["tfidf_score"],
            "matched_skills_count": row["matched_skills_count"],
            "missing_skills_count": row["missing_skills_count"],
            "matched_skills": json.loads(row["matched_skills_json"]),
            "missing_skills": json.loads(row["missing_skills_json"]),
            "explanation": row["explanation"]
        }
    finally:
        conn.close()


def delete_analysis(analysis_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Deletes an analysis record by ID.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_history WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
