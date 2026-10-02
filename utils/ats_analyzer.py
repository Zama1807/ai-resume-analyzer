"""
ATS-Oriented Resume Auditor
============================
Evaluates resume readiness against Applicant Tracking Systems (ATS) heuristics:
- Section completeness & standard headings
- Contact info availability
- Keyword & technical skills coverage
- Formatting, page count, and length checks
- Honest evaluation without false guarantees
"""

from typing import Dict, Any, List

# Standard essential sections expected by ATS parsers
ESSENTIAL_SECTIONS = ["skills", "experience", "education", "projects"]

# Action verbs commonly looked for by ATS and recruiters
ACTION_VERBS = {
    "developed", "built", "implemented", "designed", "created", "engineered",
    "optimized", "automated", "integrated", "deployed", "led", "managed",
    "reduced", "increased", "accelerated", "configured", "maintained",
    "researched", "collaborated", "achieved", "delivered", "trained"
}

def analyze_ats_compliance(resume_data: Dict[str, Any], job_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Performs an ATS compliance audit on the parsed resume.
    Optionally incorporates job description data for skill & keyword coverage.
    """
    cleaned_text = resume_data.get("cleaned_text", "")
    sections = resume_data.get("sections", {})
    contact = resume_data.get("contact_info", {})
    page_count = resume_data.get("page_count", 1)
    word_count = resume_data.get("word_count", 0)

    # 1. Section Completeness Audit (Weight: 35%)
    section_checks = {}
    found_sections_count = 0

    for sec in ESSENTIAL_SECTIONS:
        has_sec = bool(sections.get(sec) and len(sections[sec].strip()) > 15)
        if has_sec:
            found_sections_count += 1
            section_checks[sec] = {
                "status": "PASS",
                "message": f"Standard '{sec.title()}' section clearly identified."
            }
        else:
            section_checks[sec] = {
                "status": "MISSING",
                "message": f"'{sec.title()}' section is missing or uses non-standard headings."
            }

    # Summary is optional but recommended
    has_summary = bool(sections.get("summary") and len(sections["summary"].strip()) > 10)
    section_checks["summary"] = {
        "status": "PASS" if has_summary else "OPTIONAL",
        "message": "Professional Summary detected." if has_summary else "Summary section is missing (optional but helpful)."
    }

    completeness_score = (found_sections_count / len(ESSENTIAL_SECTIONS)) * 100.0

    # 2. Formatting & Structure Audit (Weight: 25%)
    formatting_issues = []
    formatting_score = 100.0

    # Page count check
    if page_count == 1 or page_count == 2:
        formatting_issues.append({
            "check": "Page Count",
            "status": "PASS",
            "message": f"Ideal resume length: {page_count} page(s)."
        })
    else:
        formatting_score -= 20.0
        formatting_issues.append({
            "check": "Page Count",
            "status": "WARNING",
            "message": f"Resume is {page_count} pages. For entry/mid levels, 1-2 pages is recommended."
        })

    # Word count check
    if 180 <= word_count <= 950:
        formatting_issues.append({
            "check": "Word Density",
            "status": "PASS",
            "message": f"Good text density ({word_count} words). Concise and parser-friendly."
        })
    elif word_count < 180:
        formatting_score -= 25.0
        formatting_issues.append({
            "check": "Word Density",
            "status": "WARNING",
            "message": f"Resume has only {word_count} words. It may be too brief to demonstrate required competencies."
        })
    else:
        formatting_score -= 15.0
        formatting_issues.append({
            "check": "Word Density",
            "status": "WARNING",
            "message": f"Resume has {word_count} words. Consider condensing to keep it under 800 words."
        })

    # Contact Info check
    missing_contacts = []
    if not contact.get("email") or contact["email"] == "Not Detected":
        missing_contacts.append("Email")
    if not contact.get("phone") or contact["phone"] == "Not Detected":
        missing_contacts.append("Phone")

    if not missing_contacts:
        formatting_issues.append({
            "check": "Contact Information",
            "status": "PASS",
            "message": "Essential contact details (Email and Phone) were cleanly detected."
        })
    else:
        formatting_score -= 30.0
        formatting_issues.append({
            "check": "Contact Information",
            "status": "FAIL",
            "message": f"Critical contact details not found: {', '.join(missing_contacts)}."
        })

    # Action Verbs check
    text_lower = cleaned_text.lower()
    found_verbs = [v for v in ACTION_VERBS if v in text_lower]
    if len(found_verbs) >= 4:
        formatting_issues.append({
            "check": "Action Verbs",
            "status": "PASS",
            "message": f"Strong impact verbs detected ({', '.join(found_verbs[:5])})."
        })
    else:
        formatting_score -= 10.0
        formatting_issues.append({
            "check": "Action Verbs",
            "status": "WARNING",
            "message": "Few strong action verbs detected. Use verbs like 'developed', 'optimized', 'engineered'."
        })

    formatting_score = max(0.0, formatting_score)

    # 3. Skills Coverage (Weight: 25%) & Keyword Coverage (Weight: 15%)
    if job_data and job_data.get("success"):
        job_req = set(job_data.get("required_skills", []))
        cand_skills = set(resume_data.get("skills_analysis", {}).get("all_skills", []))
        
        if job_req:
            matched_skills_count = len(cand_skills.intersection(job_req))
            skills_coverage = (matched_skills_count / len(job_req)) * 100.0
        else:
            skills_coverage = 80.0

        job_kws = job_data.get("top_keywords", [])
        if job_kws:
            matched_kws_count = sum(1 for kw in job_kws if kw.lower() in text_lower)
            keyword_coverage = (matched_kws_count / len(job_kws)) * 100.0
        else:
            keyword_coverage = 70.0

        # Weighted ATS Composite Score
        ats_score = (
            (0.35 * completeness_score) +
            (0.25 * formatting_score) +
            (0.25 * skills_coverage) +
            (0.15 * keyword_coverage)
        )
    else:
        # Resume-only baseline ATS score
        skills_coverage = None
        keyword_coverage = None
        ats_score = (0.60 * completeness_score) + (0.40 * formatting_score)

    ats_score = round(max(0.0, min(100.0, ats_score)), 1)

    return {
        "ats_score": ats_score,
        "section_audit": section_checks,
        "formatting_audit": formatting_issues,
        "metrics": {
            "completeness_score": round(completeness_score, 1),
            "formatting_score": round(formatting_score, 1),
            "skills_coverage": round(skills_coverage, 1) if skills_coverage is not None else "N/A",
            "keyword_coverage": round(keyword_coverage, 1) if keyword_coverage is not None else "N/A"
        },
        "disclaimer": (
            "Notice: This ATS evaluation uses standard automated parsing heuristics (section headers, "
            "contact regex, word density, and keyword frequency). Real Applicant Tracking Systems vary "
            "widely by employer. This score is an optimization benchmark and does not guarantee interview selection."
        )
    }
