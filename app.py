"""
AI Resume Analyzer & Job Match Assistant
=========================================
Main Streamlit Application Entrypoint.
Production-Grade Interactive Web UI with Plotly Visualizations & SQLite Persistence.
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.pdf_parser import parse_pdf
from utils.text_cleaner import clean_text
from utils.skill_extractor import extract_skills, SKILL_TAXONOMY
from utils.job_analyzer import analyze_job_description
from utils.matcher import calculate_match, compute_tfidf_similarity
from utils.ats_analyzer import analyze_ats_compliance
from utils.recommendations import recommend_roles, generate_improvement_suggestions
from utils.database import init_db, save_analysis, get_all_analyses, delete_analysis

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Analyzer & Job Match Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize local SQLite database
init_db()

# --- Initialize Session State ---
if "resume_data" not in st.session_state:
    st.session_state["resume_data"] = None

if "job_data" not in st.session_state:
    st.session_state["job_data"] = None

if "match_data" not in st.session_state:
    st.session_state["match_data"] = None

if "ats_data" not in st.session_state:
    st.session_state["ats_data"] = None

# --- Pre-configured Sample Job Descriptions for Quick Testing ---
SAMPLE_JDS = {
    "Python Full-Stack Developer": """Job Title: Python Full Stack Developer
Company: Innovatech Labs
Location: Remote / Hybrid

About the Role:
We are seeking an energetic Full Stack Developer to build high-performance web APIs and cloud microservices. You will collaborate with cross-functional product teams to design scalable architectures.

Minimum Requirements:
- 1-3 years of experience in Python web development.
- Strong proficiency in FastAPI, Django, and SQL.
- Hands-on experience with PostgreSQL, Git, and REST APIs.
- Familiarity with unit testing and Pytest.
- Bachelor's degree in Computer Science or equivalent engineering background.

Preferred Qualifications:
- Experience with Docker, Redis, and React.
- Familiarity with AWS cloud deployment (S3, EC2) and CI/CD pipelines.
- Knowledge of agile methodologies and microservice architectures.
""",
    "Machine Learning & AI Engineer": """Job Title: Machine Learning Engineer
Company: Cognitive Cloud AI
Location: Bangalore / Hybrid

About the Role:
Join our AI research team deploying predictive models and NLP pipelines into production. You will develop automated pipelines for model training, evaluation, and serving.

Requirements:
- Bachelor's or Master's degree in Computer Science, Data Science, or related field.
- 2+ years experience building ML pipelines with Python.
- Strong knowledge of PyTorch, TensorFlow, Scikit-learn, and Pandas.
- Proven expertise in Natural Language Processing (NLP) or Computer Vision.
- Solid understanding of SQL and data preprocessing.

Preferred Skills:
- Experience with Docker, Kubernetes, and FastAPI for model serving.
- Experience with Hugging Face transformers and Large Language Models (LLMs).
- Cloud experience on AWS or Google Cloud.
""",
    "DevOps & Cloud Systems Specialist": """Job Title: Cloud & DevOps Engineer
Company: Scalable Systems Inc
Location: Remote

About the Role:
We are looking for a Cloud Infrastructure Engineer to manage Kubernetes clusters and automated CI/CD deployment pipelines.

Requirements:
- Strong experience with Linux systems administration and Bash scripting.
- Practical experience with Docker and Kubernetes cluster management.
- Hands-on expertise with AWS or Microsoft Azure.
- Automated CI/CD experience with GitHub Actions or Jenkins.
- Experience with Terraform infrastructure as code.

Preferred:
- Scripting ability in Python or Go.
- Experience with PostgreSQL or Redis database administration.
- Monitoring tools such as Prometheus, Grafana, or Datadog.
"""
}

# --- Custom Styling for a Clean, Professional UI ---
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 13px;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Candidate & Job Info Card */
    .info-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-left: 5px solid #1f77b4;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    
    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 14px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .badge-primary { background-color: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb; }
    .badge-required { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
    .badge-preferred { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    .badge-info { background-color: #e1f5fe; color: #0277bd; border: 1px solid #b3e5fc; }
    .badge-secondary { background-color: #f5f5f5; color: #424242; border: 1px solid #e0e0e0; }
    
    /* Box Container */
    .category-box {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }
    .category-title {
        font-weight: 700;
        font-size: 15px;
        color: #333333;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=70)
    st.title("AI Career Matcher")
    st.caption("AI-Powered Resume & Job Fit Engine")
    st.markdown("---")
    
    # Active State Indicators
    if st.session_state["resume_data"] and st.session_state["resume_data"].get("success"):
        c_name = st.session_state["resume_data"]["contact_info"].get("name", "Active Candidate")
        total_s = st.session_state["resume_data"].get("skills_analysis", {}).get("total_skills_found", 0)
        st.success(f"📄 **Resume:** {c_name} ({total_s} skills)")
    else:
        st.info("ℹ️ No resume uploaded yet.")

    if st.session_state["job_data"] and st.session_state["job_data"].get("success"):
        role_t = st.session_state["job_data"].get("role_title", "Target Role")
        req_cnt = len(st.session_state["job_data"].get("required_skills", []))
        st.success(f"💼 **Job Target:** {role_t} ({req_cnt} req skills)")
    else:
        st.info("ℹ️ No target job analyzed yet.")

    # Auto-Calculate Match whenever both are ready
    if st.session_state["resume_data"] and st.session_state["job_data"]:
        if st.session_state["match_data"] is None:
            st.session_state["match_data"] = calculate_match(st.session_state["resume_data"], st.session_state["job_data"])
        if st.session_state["ats_data"] is None:
            st.session_state["ats_data"] = analyze_ats_compliance(st.session_state["resume_data"], st.session_state["job_data"])

    menu_choice = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📄 Resume Analyzer",
            "💼 Job Description",
            "🎯 Match Analysis",
            "🛡️ ATS Audit & Compliance",
            "💡 Recommendations & Roles",
            "🕒 Analysis History",
            "ℹ️ About & System Info"
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption("Developed by Final-Year Computer Science & Design Student.")

# ==========================================
# VIEW 1: DASHBOARD
# ==========================================
if menu_choice == "📊 Dashboard":
    st.header("📊 Executive Analytics Dashboard")
    st.write(
        "Evaluate candidates against real industry job descriptions using **transparent NLP, "
        "TF-IDF cosine similarity, and skill taxonomy matching**—100% free, open-source, and explainable."
    )
    
    resume_data = st.session_state["resume_data"]
    job_data = st.session_state["job_data"]
    match_data = st.session_state["match_data"]
    ats_data = st.session_state["ats_data"]
    
    # Top KPI Metrics Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        score_val = f"{match_data['overall_match_score']}%" if match_data else "N/A"
        st.markdown(f'<div class="metric-card"><div class="metric-value">{score_val}</div><div class="metric-label">Overall Match Score</div></div>', unsafe_allow_html=True)
    with k2:
        tfidf_val = f"{match_data['tfidf_score']}%" if match_data else "N/A"
        st.markdown(f'<div class="metric-card"><div class="metric-value">{tfidf_val}</div><div class="metric-label">TF-IDF Similarity</div></div>', unsafe_allow_html=True)
    with k3:
        skills_matched = f"{len(match_data['matched_required_skills'])} / {len(job_data['required_skills'])}" if (match_data and job_data) else "N/A"
        st.markdown(f'<div class="metric-card"><div class="metric-value">{skills_matched}</div><div class="metric-label">Required Skills Matched</div></div>', unsafe_allow_html=True)
    with k4:
        ats_val = f"{ats_data['ats_score']}%" if ats_data else "N/A"
        st.markdown(f'<div class="metric-card"><div class="metric-value">{ats_val}</div><div class="metric-label">ATS Readiness Score</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    if resume_data and job_data and match_data:
        # Visual Analytics
        c_col1, c_col2 = st.columns([1, 1])
        
        with c_col1:
            st.subheader("🎯 Overall Match Indicator")
            score = match_data["overall_match_score"]
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Match Rating", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 40], 'color': "#ffebee"},
                        {'range': [40, 70], 'color': "#fff8e1"},
                        {'range': [70, 100], 'color': "#e8f5e9"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 3},
                        'thickness': 0.75,
                        'value': score
                    }
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with c_col2:
            st.subheader("📊 Skill Overlap Breakdown")
            df_match = pd.DataFrame({
                "Metric": ["Required Matched", "Required Missing", "Preferred Matched", "Preferred Missing"],
                "Count": [
                    len(match_data["matched_required_skills"]),
                    len(match_data["missing_required_skills"]),
                    len(match_data["matched_preferred_skills"]),
                    len(match_data["missing_preferred_skills"])
                ]
            })
            fig_bar = px.bar(
                df_match,
                x="Metric",
                y="Count",
                color="Metric",
                color_discrete_map={
                    "Required Matched": "#2e7d32",
                    "Required Missing": "#c62828",
                    "Preferred Matched": "#0277bd",
                    "Preferred Missing": "#f57f17"
                }
            )
            fig_bar.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.info(f"💡 **Explainability Note:** {match_data['explanation']}")

    else:
        st.warning("👉 To generate full match analytics, please upload a resume in **'📄 Resume Analyzer'** and enter a job description in **'💼 Job Description'**.")


# ==========================================
# VIEW 2: RESUME ANALYZER
# ==========================================
elif menu_choice == "📄 Resume Analyzer":
    st.header("📄 Resume Upload & Structured Ingestion")
    st.write("Upload a PDF resume to extract contact information, logical sections, and categorized skills.")

    upload_col, sample_col = st.columns([3, 1])
    with upload_col:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF only, max 5MB):",
            type=["pdf"],
            help="Upload a standard PDF resume exported from Word, Canva, or LaTeX."
        )
    with sample_col:
        st.write("&nbsp;")
        load_sample = st.button("💡 Load Sample Resume", help="Click to load a pre-built sample resume to test immediately.")

    file_to_process = None
    if uploaded_file is not None:
        file_to_process = uploaded_file
    elif load_sample:
        sample_path = os.path.join("assets", "sample_resume.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_to_process = f.read()
        else:
            st.error("Sample resume file not found at `assets/sample_resume.pdf`.")

    if file_to_process:
        with st.spinner("Extracting text, sections, and technical skills..."):
            parsed_result = parse_pdf(file_to_process)
            
            if parsed_result["success"]:
                parsed_result["skills_analysis"] = extract_skills(parsed_result["cleaned_text"])
                st.session_state["resume_data"] = parsed_result
                # Reset match and ats caches
                st.session_state["match_data"] = None
                st.session_state["ats_data"] = None
                st.success("✅ Resume parsed and skills categorized successfully!")
            else:
                st.session_state["resume_data"] = None
                st.error(f"❌ {parsed_result['error_message']}")

    resume_data = st.session_state.get("resume_data")
    if resume_data and resume_data.get("success"):
        st.markdown("---")
        
        contact = resume_data["contact_info"]
        st.markdown(f"""
        <div class="info-card">
            <h3 style="margin-top:0; color:#1f77b4;">👤 {contact.get('name', 'Candidate Profile')}</h3>
            <span class="badge badge-info">📧 {contact.get('email', 'Email Not Detected')}</span>
            <span class="badge badge-info">📞 {contact.get('phone', 'Phone Not Detected')}</span>
            <span class="badge badge-secondary">🔗 {contact.get('linkedin', 'LinkedIn Not Detected')}</span>
            <span class="badge badge-secondary">💻 {contact.get('github', 'GitHub Not Detected')}</span>
        </div>
        """, unsafe_allow_html=True)

        skills_info = resume_data.get("skills_analysis", {})
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Pages", resume_data["page_count"])
        m2.metric("Extracted Words", resume_data["word_count"])
        m3.metric("Detected Sections", f"{len(resume_data['detected_sections_list'])} / 6")
        m4.metric("Technical Skills Found", skills_info.get("total_skills_found", 0))

        st.markdown("---")
        st.subheader("📑 Parsed Section Inspector")
        
        tab_skills, tab_exp, tab_edu, tab_proj, tab_cert, tab_full = st.tabs([
            "⚡ Extracted Skills",
            "💼 Experience",
            "🎓 Education",
            "🚀 Projects",
            "📜 Certifications",
            "🔍 Raw Cleaned Text"
        ])
        
        sections = resume_data["sections"]
        
        with tab_skills:
            st.write("#### Categorized Technical Skills Detected by NLP Engine")
            cat_skills = skills_info.get("categorized_skills", {})
            for cat, s_list in cat_skills.items():
                if s_list:
                    badge_html = "".join([f'<span class="badge badge-primary">{s}</span>' for s in s_list])
                    st.markdown(f"""
                    <div class="category-box">
                        <div class="category-title">{cat} ({len(s_list)})</div>
                        {badge_html}
                    </div>
                    """, unsafe_allow_html=True)

        with tab_exp:
            if sections.get("experience"):
                st.markdown(sections["experience"])
            else:
                st.info("No dedicated 'Work Experience' section detected.")
        
        with tab_edu:
            if sections.get("education"):
                st.markdown(sections["education"])
            else:
                st.info("No dedicated 'Education' section detected.")
                
        with tab_proj:
            if sections.get("projects"):
                st.markdown(sections["projects"])
            else:
                st.info("No dedicated 'Projects' section detected.")
                
        with tab_cert:
            if sections.get("certifications"):
                st.markdown(sections["certifications"])
            else:
                st.info("No separate 'Certifications' section detected.")

        with tab_full:
            st.text_area(
                "Full Normalized Resume Text (Ready for NLP Processing):",
                resume_data["cleaned_text"],
                height=300
            )


# ==========================================
# VIEW 3: JOB DESCRIPTION
# ==========================================
elif menu_choice == "💼 Job Description":
    st.header("💼 Target Job Description Ingestion & Parsing")
    st.write("Paste an active job posting or select one of the pre-configured industry templates.")

    st.write("##### Quick Load Pre-configured Target Roles:")
    t_col1, t_col2, t_col3 = st.columns(3)
    
    selected_template = None
    with t_col1:
        if st.button("🐍 Python Full-Stack Dev"):
            selected_template = SAMPLE_JDS["Python Full-Stack Developer"]
    with t_col2:
        if st.button("🤖 Machine Learning / AI"):
            selected_template = SAMPLE_JDS["Machine Learning & AI Engineer"]
    with t_col3:
        if st.button("☁️ DevOps & Cloud Specialist"):
            selected_template = SAMPLE_JDS["DevOps & Cloud Systems Specialist"]

    current_default = selected_template if selected_template else (
        st.session_state["job_data"]["cleaned_text"] if (st.session_state["job_data"] and st.session_state["job_data"].get("success")) else ""
    )

    jd_text = st.text_area(
        "Paste Job Description Text here:",
        value=current_default,
        height=220,
        help="Paste the full job posting including roles, requirements, and responsibilities."
    )

    if st.button("🔍 Analyze Job Description", type="primary"):
        if not jd_text.strip():
            st.error("Please enter or paste a job description before analyzing.")
        else:
            with st.spinner("Analyzing requirements, parsing role title, and partitioning skills..."):
                job_res = analyze_job_description(jd_text)
                if job_res["success"]:
                    st.session_state["job_data"] = job_res
                    # Reset match cache
                    st.session_state["match_data"] = None
                    st.session_state["ats_data"] = None
                    st.success("✅ Job Description parsed and categorized successfully!")
                else:
                    st.session_state["job_data"] = None
                    st.error(f"❌ {job_res['error_message']}")

    job_data = st.session_state.get("job_data")
    if job_data and job_data.get("success"):
        st.markdown("---")
        
        st.markdown(f"""
        <div class="info-card">
            <h3 style="margin-top:0; color:#1f77b4;">💼 Target Role: {job_data['role_title']}</h3>
            <span class="badge badge-info">⏱️ Experience: {job_data['experience_required']}</span>
            <span class="badge badge-secondary">🎓 Education: {job_data['education_required']}</span>
        </div>
        """, unsafe_allow_html=True)

        j1, j2, j3, j4 = st.columns(4)
        j1.metric("Total Words", job_data["word_count"])
        j2.metric("Required Skills", len(job_data["required_skills"]))
        j3.metric("Preferred Skills", len(job_data["preferred_skills"]))
        j4.metric("Extracted Keywords", len(job_data["top_keywords"]))

        st.markdown("---")
        
        req_col, pref_col = st.columns(2)
        with req_col:
            st.subheader("🔴 Core / Required Skills (Must-Have)")
            if job_data["required_skills"]:
                r_badges = "".join([f'<span class="badge badge-required">{s}</span>' for s in job_data["required_skills"]])
                st.markdown(f'<div class="category-box">{r_badges}</div>', unsafe_allow_html=True)
            else:
                st.info("No specific must-have technical skills detected.")

        with pref_col:
            st.subheader("🟢 Preferred / Nice-To-Have Skills (Bonus)")
            if job_data["preferred_skills"]:
                p_badges = "".join([f'<span class="badge badge-preferred">{s}</span>' for s in job_data["preferred_skills"]])
                st.markdown(f'<div class="category-box">{p_badges}</div>', unsafe_allow_html=True)
            else:
                st.info("No separate preferred/bonus skills detected.")

        st.markdown("---")
        st.subheader("🔑 Critical Job Domain Keywords")
        kw_badges = "".join([f'<span class="badge badge-secondary">{kw}</span>' for kw in job_data["top_keywords"]])
        st.markdown(f'<div class="category-box">{kw_badges}</div>', unsafe_allow_html=True)


# ==========================================
# VIEW 4: MATCH ANALYSIS
# ==========================================
elif menu_choice == "🎯 Match Analysis":
    st.header("🎯 Resume vs Job Match Analysis")
    
    resume_data = st.session_state.get("resume_data")
    job_data = st.session_state.get("job_data")
    
    if not resume_data or not job_data:
        st.warning("⚠️ Both a Resume and a Job Description must be loaded to run matching.")
        st.info("Please complete **'📄 Resume Analyzer'** and **'💼 Job Description'** first.")
    else:
        if st.session_state.get("match_data") is None:
            st.session_state["match_data"] = calculate_match(resume_data, job_data)
        
        match = st.session_state["match_data"]
        
        # Match Banner with Score & Rating
        score = match["overall_match_score"]
        if score >= 75:
            match_tier = "🌟 Exceptional Match"
            alert_func = st.success
        elif score >= 60:
            match_tier = "✅ Strong Competitive Match"
            alert_func = st.info
        elif score >= 40:
            match_tier = "⚠️ Moderate Match — Skill Gaps Present"
            alert_func = st.warning
        else:
            match_tier = "❌ Low Match — Significant Up-skilling Needed"
            alert_func = st.error

        alert_func(f"### {match_tier}: **{score}%** Overall Alignment")
        st.caption(match["explanation"])

        # Quick Save to SQLite Button
        save_col1, save_col2 = st.columns([3, 1])
        with save_col2:
            if st.button("💾 Save Session to History"):
                record_id = save_analysis(
                    candidate_name=resume_data["contact_info"].get("name", "Candidate"),
                    candidate_email=resume_data["contact_info"].get("email", ""),
                    job_role=job_data.get("role_title", "Role"),
                    overall_score=match["overall_match_score"],
                    tfidf_score=match["tfidf_score"],
                    matched_skills=match["all_matched_skills"],
                    missing_skills=match["all_missing_skills"],
                    explanation=match["explanation"]
                )
                st.success(f"Analysis saved to database (Audit ID: #{record_id})!")

        st.markdown("---")

        # Detailed Match Tabs
        tab_skills, tab_missing, tab_kw, tab_math = st.tabs([
            "✅ Matched Skills",
            "❌ Missing Skills & Gaps",
            "🔑 Domain Keywords Overlap",
            "🔬 Mathematical Breakdown"
        ])

        with tab_skills:
            st.subheader("Technical Competencies Found in Both Resume & Job")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.write("##### Core / Required Skills Matched:")
                if match["matched_required_skills"]:
                    b_html = "".join([f'<span class="badge badge-required">{s}</span>' for s in match["matched_required_skills"]])
                    st.markdown(f'<div class="category-box">{b_html}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No core required skills matched.")

            with col_m2:
                st.write("##### Preferred / Bonus Skills Matched:")
                if match["matched_preferred_skills"]:
                    p_html = "".join([f'<span class="badge badge-preferred">{s}</span>' for s in match["matched_preferred_skills"]])
                    st.markdown(f'<div class="category-box">{p_html}</div>', unsafe_allow_html=True)
                else:
                    st.info("No preferred bonus skills matched.")

            if match["bonus_candidate_skills"]:
                st.write("##### Additional Candidate Technical Skills (Not explicitly requested):")
                extra_html = "".join([f'<span class="badge badge-primary">{s}</span>' for s in match["bonus_candidate_skills"][:15]])
                st.markdown(f'<div class="category-box">{extra_html}</div>', unsafe_allow_html=True)

        with tab_missing:
            st.subheader("Skill Deficiencies & Target Opportunities")
            col_x1, col_x2 = st.columns(2)
            with col_x1:
                st.write("##### Critical Missing Required Skills (Dealbreakers):")
                if match["missing_required_skills"]:
                    x_html = "".join([f'<span class="badge badge-required">{s}</span>' for s in match["missing_required_skills"]])
                    st.markdown(f'<div class="category-box">{x_html}</div>', unsafe_allow_html=True)
                else:
                    st.success("🎉 You possess 100% of the core required skills!")

            with col_x2:
                st.write("##### Missing Preferred / Bonus Skills:")
                if match["missing_preferred_skills"]:
                    px_html = "".join([f'<span class="badge badge-preferred">{s}</span>' for s in match["missing_preferred_skills"]])
                    st.markdown(f'<div class="category-box">{px_html}</div>', unsafe_allow_html=True)
                else:
                    st.success("🎉 You possess all preferred bonus skills!")

        with tab_kw:
            st.subheader("Domain & Operational Keywords Overlap")
            kw_col1, kw_col2 = st.columns(2)
            with kw_col1:
                st.write("##### Keywords Found in Resume:")
                if match["matched_keywords"]:
                    km_html = "".join([f'<span class="badge badge-info">{k}</span>' for k in match["matched_keywords"]])
                    st.markdown(f'<div class="category-box">{km_html}</div>', unsafe_allow_html=True)
                else:
                    st.info("No exact domain keywords detected.")

            with kw_col2:
                st.write("##### Important Job Keywords Missing:")
                if match["missing_keywords"]:
                    kmis_html = "".join([f'<span class="badge badge-secondary">{k}</span>' for k in match["missing_keywords"]])
                    st.markdown(f'<div class="category-box">{kmis_html}</div>', unsafe_allow_html=True)
                else:
                    st.success("All primary job keywords are present!")

        with tab_math:
            st.subheader("Mathematical Scoring Transparency")
            st.markdown("""
            Unlike black-box AI tools that invent percentages, our scoring engine is **100% deterministic and auditable**:
            """)
            st.write(f"- **TF-IDF Cosine Similarity:** `{match['tfidf_score']}%` (Evaluates full document vocabulary and semantic ngram overlap).")
            st.write(f"- **Required Skills Score:** `{match['required_skills_score']}%` ({len(match['matched_required_skills'])} matched / {len(job_data['required_skills'])} total).")
            st.write(f"- **Preferred Skills Score:** `{match['preferred_skills_score']}%` ({len(match['matched_preferred_skills'])} matched / {len(job_data['preferred_skills'])} total).")
            st.write(f"- **Keyword Coverage:** `{match['keyword_coverage_score']}%` ({len(match['matched_keywords'])} matched / {len(job_data['top_keywords'])} total).")


# ==========================================
# VIEW 5: ATS AUDIT & COMPLIANCE
# ==========================================
elif menu_choice == "🛡️ ATS Audit & Compliance":
    st.header("🛡️ ATS Parser Audit & Formatting Compliance")
    
    resume_data = st.session_state.get("resume_data")
    job_data = st.session_state.get("job_data")
    
    if not resume_data:
        st.warning("⚠️ Please upload a resume in **'📄 Resume Analyzer'** to run the ATS compliance audit.")
    else:
        if st.session_state.get("ats_data") is None:
            st.session_state["ats_data"] = analyze_ats_compliance(resume_data, job_data)
        
        ats = st.session_state["ats_data"]
        
        st.metric("ATS Readiness Score", f"{ats['ats_score']}%", help="Calculated based on standard ATS parser heuristics.")
        st.progress(int(ats['ats_score']))
        
        st.markdown("---")
        st.subheader("📋 Section Completeness Audit")
        sec_audit = ats["section_audit"]
        s_cols = st.columns(len(sec_audit))
        for i, (sec, info) in enumerate(sec_audit.items()):
            with s_cols[i]:
                if info["status"] == "PASS":
                    st.success(f"**{sec.title()}**\n\n✅ Identified")
                elif info["status"] == "OPTIONAL":
                    st.info(f"**{sec.title()}**\n\nℹ️ Optional")
                else:
                    st.error(f"**{sec.title()}**\n\n❌ Missing")

        st.markdown("---")
        st.subheader("🔍 Formatting & Structural Checks")
        for check in ats["formatting_audit"]:
            if check["status"] == "PASS":
                st.write(f"✅ **{check['check']}:** {check['message']}")
            elif check["status"] == "WARNING":
                st.write(f"⚠️ **{check['check']}:** {check['message']}")
            else:
                st.write(f"❌ **{check['check']}:** {check['message']}")

        st.markdown("---")
        st.caption(f"📌 **Disclaimer:** {ats['disclaimer']}")


# ==========================================
# VIEW 6: RECOMMENDATIONS & CAREER ROLES
# ==========================================
elif menu_choice == "💡 Recommendations & Roles":
    st.header("💡 Personalized Career Recommendations")
    
    resume_data = st.session_state.get("resume_data")
    match_data = st.session_state.get("match_data")
    
    if not resume_data:
        st.warning("⚠️ Please upload a resume in **'📄 Resume Analyzer'** to generate recommendations.")
    else:
        cand_skills = resume_data.get("skills_analysis", {}).get("all_skills", [])
        
        rec_tab1, rec_tab2 = st.tabs(["🚀 Recommended Career Roles", "📝 Resume Optimization Suggestions"])
        
        with rec_tab1:
            st.subheader("Data-Driven Role Suitability")
            st.write("Ranked by algorithmic alignment between your skills and industry role profiles:")
            
            roles = recommend_roles(cand_skills)
            
            # Interactive Bar Chart of Roles
            df_roles = pd.DataFrame(roles)
            fig_roles = px.bar(
                df_roles,
                x="match_score",
                y="role",
                orientation="h",
                color="match_score",
                color_continuous_scale="Viridis",
                title="Career Role Alignment Rating (%)"
            )
            fig_roles.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_roles, use_container_width=True)

            for r in roles:
                with st.expander(f"💼 **{r['role']}** — Match: **{r['match_score']}%**"):
                    st.write(f"*{r['description']}*")
                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        st.write("✅ **Matching Skills You Possess:**")
                        st.write(", ".join(r["matched_skills"]) if r["matched_skills"] else "None yet")
                    with r_col2:
                        st.write("🎯 **Skills to Acquire to Qualify:**")
                        st.write(", ".join(r["skills_to_acquire"]) if r["skills_to_acquire"] else "None! You meet all core requirements.")

        with rec_tab2:
            st.subheader("Honest Resume Optimization Tips")
            suggestions = generate_improvement_suggestions(resume_data, match_data)
            
            st.write("#### 🎯 Priority Skills to Learn:")
            if suggestions["skills_to_learn"]:
                for s in suggestions["skills_to_learn"]:
                    st.info(f"💡 {s}")
            else:
                st.write("No urgent missing skills identified.")

            st.write("#### 📝 Truthful Keyword Alignment:")
            if suggestions["keyword_improvements"]:
                for k in suggestions["keyword_improvements"]:
                    st.write(f"👉 {k}")

            st.write("#### 📑 Section & Readability Enhancements:")
            for e in suggestions["section_enhancements"] + suggestions["impact_and_readability"]:
                st.write(f"• {e}")


# ==========================================
# VIEW 7: ANALYSIS HISTORY
# ==========================================
elif menu_choice == "🕒 Analysis History":
    st.header("🕒 Historical Analysis Audit Trail")
    st.write("All completed sessions are persisted in a local SQLite database (`data/database.db`).")

    history = get_all_analyses()
    if not history:
        st.info("No saved analysis sessions found. Run a match in **'🎯 Match Analysis'** and click 'Save Session to History'.")
    else:
        st.write(f"Found **{len(history)}** saved record(s).")
        
        # Summary Table
        summary_rows = []
        for rec in history:
            summary_rows.append({
                "ID": rec["id"],
                "Date": rec["created_at"],
                "Candidate": rec["candidate_name"],
                "Target Role": rec["job_role"],
                "Match Score": f"{rec['overall_score']}%",
                "TF-IDF": f"{rec['tfidf_score']}%",
                "Skills Matched": rec["matched_skills_count"],
                "Skills Missing": rec["missing_skills_count"]
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

        st.markdown("---")
        st.subheader("Inspect or Manage Past Sessions")
        for rec in history:
            with st.expander(f"Audit #{rec['id']}: {rec['candidate_name']} vs {rec['job_role']} ({rec['overall_score']}%) — {rec['created_at']}"):
                st.write(f"**Explanation:** {rec['explanation']}")
                h1, h2 = st.columns(2)
                with h1:
                    st.write("**Matched Skills:**", ", ".join(rec["matched_skills"]))
                with h2:
                    st.write("**Missing Skills:**", ", ".join(rec["missing_skills"]))
                
                if st.button(f"🗑️ Delete Record #{rec['id']}", key=f"del_{rec['id']}"):
                    delete_analysis(rec["id"])
                    st.success(f"Record #{rec['id']} deleted!")
                    st.rerun()


# ==========================================
# VIEW 8: ABOUT & SYSTEM INFO
# ==========================================
elif menu_choice == "ℹ️ About & System Info":
    st.header("ℹ️ About This Project")
    st.markdown(r"""
    ### 🎯 AI Resume Analyzer & Job Match Assistant
    A real-world full-stack portfolio application developed for placement interviews and recruiter presentations.

    #### 🌟 Key Technical Highlights:
    1. **100% Free & Open-Source**: Zero paid third-party APIs, OpenAI keys, or external subscription services.
    2. **Deterministic & Explainable**: Mathematical TF-IDF Vectorization and Cosine Similarity ($S_{tfidf} \in [0, 100]$) combined with set-theoretic skill intersection.
    3. **Resilient NLP Tokenizer**: Supports C++, C#, .NET, Vue.js, and multi-word n-gram entities with automatic alias resolution.
    4. **Safety & Privacy**: Local SQLite parameterized queries to prevent SQL injection; no sensitive candidate files are uploaded to third-party clouds.
    
    #### 🛠️ Tech Stack & Responsibilities:
    - **Streamlit**: Modern interactive web interface.
    - **PyMuPDF (`fitz`)**: Fast, lossless in-memory PDF text extraction.
    - **Scikit-learn**: TF-IDF vectorization and cosine similarity matching.
    - **Plotly**: Interactive data visualizations, gauges, and comparison charts.
    - **SQLite**: Local relational database for persistent session history.
    - **Pandas**: Structured tabular manipulation.
    - **Pytest**: Automated test suite with 19 test cases.
    """)
    st.markdown("---")
    st.subheader("System Environment")
    st.write(f"- **Python Version:** `{sys.version.split()[0]}`")
    st.write(f"- **Operating System:** `{os.name.upper()}`")
    st.write(f"- **Streamlit Version:** `{st.__version__}`")
