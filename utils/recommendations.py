"""
Resume Recommendations & Career Role Matching Engine
=====================================================
Generates data-driven resume improvement suggestions and calculates
tailored career role suitability based on detected candidate competencies.
Never fabricates metrics or advises dishonest claims.
"""

from typing import Dict, List, Any

# Target Role Skill Profiles for Dynamic Recommendations
CAREER_ROLE_PROFILES = {
    "Python Developer": {
        "core_skills": ["Python", "SQL", "Git", "REST APIs", "FastAPI", "Django"],
        "description": "Focuses on backend services, scripting, automation, and API integration using Python."
    },
    "Backend Developer": {
        "core_skills": ["Python", "Java", "Node.js", "PostgreSQL", "Redis", "Docker", "REST APIs", "Microservices"],
        "description": "Specializes in server-side logic, database architecture, and microservice communications."
    },
    "Full-Stack Web Developer": {
        "core_skills": ["JavaScript", "React", "HTML", "CSS", "Python", "Node.js", "SQL", "REST APIs"],
        "description": "Builds complete user interfaces paired with robust server-side APIs."
    },
    "Machine Learning / AI Intern": {
        "core_skills": ["Python", "Machine Learning", "Scikit-learn", "Pandas", "NumPy", "PyTorch", "TensorFlow", "NLP"],
        "description": "Develops predictive models, NLP algorithms, and experimental data pipelines."
    },
    "Data Analyst / BI Specialist": {
        "core_skills": ["SQL", "Python", "Pandas", "Data Analysis", "Data Visualization", "Power BI", "Tableau"],
        "description": "Transforms business data into actionable dashboards and statistical reports."
    },
    "Cloud & DevOps Engineer": {
        "core_skills": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "GitHub Actions", "Git", "Terraform"],
        "description": "Manages automated deployments, containerization, and cloud infrastructure reliability."
    }
}


def recommend_roles(candidate_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Evaluates candidate skills against standard career role profiles.
    Returns ranked role recommendations with genuine match scores and skill breakdowns.
    """
    cand_set = set(candidate_skills)
    recommendations = []

    for role_name, profile in CAREER_ROLE_PROFILES.items():
        core_set = set(profile["core_skills"])
        matched = cand_set.intersection(core_set)
        missing = core_set.difference(cand_set)

        match_score = (len(matched) / len(core_set)) * 100.0 if core_set else 0.0

        recommendations.append({
            "role": role_name,
            "match_score": round(match_score, 1),
            "description": profile["description"],
            "matched_skills": sorted(list(matched)),
            "skills_to_acquire": sorted(list(missing))
        })

    # Sort roles by match percentage descending
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations


def generate_improvement_suggestions(
    resume_data: Dict[str, Any], 
    match_data: Dict[str, Any] = None
) -> Dict[str, List[str]]:
    """
    Generates actionable, honest suggestions to enhance resume competitiveness.
    """
    suggestions = {
        "skills_to_learn": [],
        "keyword_improvements": [],
        "section_enhancements": [],
        "impact_and_readability": []
    }

    # 1. Missing Technical Skills (From Job Match if available)
    if match_data:
        missing_req = match_data.get("missing_required_skills", [])
        missing_pref = match_data.get("missing_preferred_skills", [])

        if missing_req:
            suggestions["skills_to_learn"].append(
                f"High Priority Skills to Learn: The target role requires {', '.join(missing_req)}. "
                "Building a hands-on project with these tools will directly boost your match rating."
            )
        if missing_pref:
            suggestions["skills_to_learn"].append(
                f"Bonus Skills to Consider: Familiarity with {', '.join(missing_pref)} was listed as preferred "
                "qualifications and can give you a competitive advantage."
            )

        # 2. Honest Keyword Incorporation
        missing_kws = match_data.get("missing_keywords", [])
        if missing_kws:
            top_missing = missing_kws[:6]
            suggestions["keyword_improvements"].append(
                f"Target Domain Terminology: The job posting frequently mentions keywords like '{', '.join(top_missing)}'. "
                "If you genuinely have experience with these concepts, make sure to highlight them in your project or experience descriptions."
            )

    # 3. Section Completeness Suggestions
    sections = resume_data.get("sections", {})
    if not sections.get("summary") or len(sections.get("summary", "").strip()) < 15:
        suggestions["section_enhancements"].append(
            "Add a 2-3 sentence Professional Summary at the top emphasizing your core domain (e.g. 'CS Graduate specializing in Full-Stack Python & Data Systems')."
        )
    if not sections.get("certifications") or len(sections.get("certifications", "").strip()) < 10:
        suggestions["section_enhancements"].append(
            "Consider adding a Certifications section with vendor credentials (AWS Cloud Practitioner, Oracle Java, or Coursera Deep Learning) to validate continuous learning."
        )

    # 4. Measurable Impact & Readability
    raw_text = resume_data.get("cleaned_text", "")
    # Check for quantitative impact numbers (e.g. 20%, $10k, 500+ users)
    import re
    has_metrics = bool(re.search(r"\b(?:\d+%(?:\s+reduction|\s+increase)?|\$\d+|\d+\+?\s+users|\d+\s+ms)\b", raw_text, re.IGNORECASE))
    
    if not has_metrics:
        suggestions["impact_and_readability"].append(
            "Quantify Project Accomplishments: Use the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'. "
            "For example: 'Reduced API response time by 25% by implementing Redis caching.'"
        )
    else:
        suggestions["impact_and_readability"].append(
            "Strong Metrics Present: You have included quantitative metrics in your descriptions. Ensure each bullet point clearly highlights business or performance impact."
        )

    # Bullet length check
    long_bullets = [line for line in raw_text.split("\n") if len(line.split()) > 35]
    if len(long_bullets) > 3:
        suggestions["impact_and_readability"].append(
            "Break Down Dense Paragraphs: Several bullet points exceed 35 words. ATS systems and human recruiters skim in 6 seconds; keep bullet points between 15-25 words."
        )

    return suggestions
