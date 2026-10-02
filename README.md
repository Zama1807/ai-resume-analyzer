# AI Resume Analyzer & Job Match Assistant 🎯

An intelligent, explainable, and production-ready career tool built with Python, Streamlit, NLP, and Scikit-learn. It extracts candidate profiles from PDF resumes, parses job descriptions, calculates transparent mathematical match scores, performs ATS compliance audits, and recommends personalized career trajectories.

---

## 📌 Problem Statement

In the modern hiring landscape, job applicants submit hundreds of resumes into corporate Applicant Tracking Systems (ATS) without understanding how well their credentials align with job descriptions. Furthermore, commercial tools often:
1. Rely on costly, opaque black-box APIs (e.g. OpenAI GPT-4) that cannot be audited.
2. Fabricate arbitrary match percentages with zero mathematical explanation.
3. Compromise privacy by transmitting sensitive personal data to third-party cloud servers.

**AI Resume Analyzer & Job Match Assistant** solves this problem by providing a 100% free, deterministic, locally auditable, and mathematically grounded resume-job alignment platform.

---

## 🌟 Key Features

1. **Robust PDF Resume Ingestion:**
   - In-memory parsing via **PyMuPDF (`fitz`)** with zero disk writes.
   - Extracts candidate Contact Information (Name, Email, Phone, LinkedIn, GitHub).
   - Segments resumes into structured logical sections (Experience, Education, Projects, Skills, Certifications).
   - Scanned/image-only PDF detection and 5MB payload limits.

2. **Extensible Categorized Skill Extraction:**
   - Pre-compiled taxonomy covering 120+ skills across **7 industry domains** (Languages, Web, Databases, Frameworks, Cloud/DevOps, AI/ML, Developer Tools).
   - Standardizes shorthand aliases (e.g. `postgres` $\rightarrow$ `PostgreSQL`, `k8s` $\rightarrow$ `Kubernetes`, `reactjs` $\rightarrow$ `React`).
   - Custom lookaround token boundary matcher preserving special tech symbols like `C++`, `C#`, `.NET`, `Vue.js`, and `CI/CD`.

3. **Intelligent Job Description Parsing:**
   - Extracts target job title, experience level, and educational criteria.
   - Automatically partitions technical competencies into **Required (Must-Have)** vs. **Preferred (Bonus)** qualifications using section boundary linguistics.
   - Filters English stopwords to identify salient domain keywords.

4. **Transparent Mathematical Matching Engine:**
   - **TF-IDF Vectorization & Cosine Similarity:** Computes semantic text overlap across unigram and bigram vocabularies.
   - **Set-Theoretic Skill Overlap:** Deterministic calculation of matched vs. missing required and preferred skills.
   - **Explainable Weighted Formula:**
     $$\text{Overall Score} = 0.50 \times S_{\text{required}} + 0.30 \times S_{\text{tfidf}} + 0.20 \times S_{\text{preferred}}$$

5. **ATS Compliance & Readability Auditor:**
   - Verifies presence of standard section headings.
   - Evaluates page count (1-2 pages), word density, and contact accessibility.
   - Audits action verb presence (`developed`, `optimized`, `engineered`).
   - Clear ethical disclaimer: does not make false guarantees of hiring success.

6. **Actionable Recommendations & Role Matching:**
   - Pinpoints high-priority missing technical skills to acquire.
   - Advises truthful domain keyword integration.
   - Dynamically evaluates candidate competencies against 6 industry career profiles (*Python Developer, Backend Developer, Full-Stack Developer, ML/AI Intern, Data Analyst, Cloud/DevOps Engineer*).

7. **Local SQLite Persistence & History Trail:**
   - Persists all analysis sessions locally in SQLite (`data/database.db`).
   - Uses parameterized queries (`?`) to prevent SQL injection.
   - Review past audits, inspect skill breakdowns, or delete records.

---

## 🛠️ Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3.11+** | Core programming language |
| **Streamlit (v1.35+)** | Responsive web application framework |
| **PyMuPDF / fitz (v1.24+)** | In-memory text extraction from PDF files |
| **Scikit-learn (v1.4+)** | TF-IDF vectorization and Cosine Similarity calculation |
| **Pandas (v2.2+)** | Data structuring, tabular display, and transformations |
| **Plotly (v5.22+)** | Interactive visualization gauges, bar charts, and donuts |
| **SQLite3** | Local relational database for session history |
| **Pytest (v8.0+)** | Automated unit testing framework |

---

## 📐 System Pipeline Architecture

```
┌──────────────────────┐        ┌───────────────────────────┐
│  Uploaded PDF Resume │        │ Target Job Description    │
└──────────┬───────────┘        └─────────────┬─────────────┘
           │                                  │
[PyMuPDF Text Extractor]            [Text Cleaner / Normalizer]
           │                                  │
[Regex / spaCy NLP Parsing]         [Requirement & Skill Parsing]
           │                                  │
           └───────────────┬──────────────────┘
                           ▼
           ┌───────────────────────────────┐
           │    Matching & Scikit Engine   │
           │  • TF-IDF Cosine Similarity   │
           │  • Exact & Semantic Skills    │
           │  • ATS Completeness Score     │
           └───────────────┬───────────────┘
                           ▼
           ┌───────────────────────────────┐
           │    Interactive Streamlit UI   │
           │  • Plotly Skill Radar / Bars  │
           │  • Honest Gap Suggestions     │
           │  • SQLite History Records     │
           └───────────────────────────────┘
```

---

## 📂 Project Structure

```text
ai_resume_analyzer/
│
├── app.py                      # Main Streamlit web application & view controller
├── requirements.txt            # Core open-source dependencies
├── .gitignore                  # Git ignore rules for venv, cache, and local DBs
├── README.md                   # Comprehensive documentation & setup guide
│
├── data/
│   ├── .gitkeep                # Git tracking marker
│   └── database.db             # Local SQLite database (auto-generated)
│
├── utils/
│   ├── __init__.py             # Utils package marker
│   ├── pdf_parser.py           # PyMuPDF ingestion, contact & section detection
│   ├── text_cleaner.py         # Unicode, whitespace, and token normalizer
│   ├── skill_extractor.py      # Extensible 7-domain taxonomy & regex matcher
│   ├── job_analyzer.py         # Job title, experience, and skill partitioner
│   ├── matcher.py              # TF-IDF cosine similarity & match scoring
│   ├── ats_analyzer.py         # Section completeness & formatting auditor
│   ├── recommendations.py      # Improvement suggestions & role recommender
│   └── database.py             # SQLite parameterized CRUD operations
│
├── assets/
│   └── sample_resume.pdf       # Pre-generated sample resume for instant testing
│
└── tests/
    ├── __init__.py             # Tests package marker
    ├── test_pdf_parser.py      # Unit tests for text cleaning and PDF parsing
    ├── test_skill_extractor.py # Unit tests for skill extraction & aliases
    ├── test_job_analyzer.py    # Unit tests for job description parsing
    ├── test_matcher.py         # Unit tests for TF-IDF & similarity scoring
    ├── test_ats_analyzer.py    # Unit tests for ATS compliance audit
    ├── test_recommendations.py # Unit tests for role ranking & suggestions
    └── test_database.py        # Unit tests for SQLite database operations
```

---

## ⚡ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Launch the Streamlit interface:
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🧪 Running Automated Unit Tests

Run the complete test suite containing **19 automated unit tests**:
```bash
pytest -v
```

Expected output:
```text
tests/test_ats_analyzer.py::test_ats_compliance_with_complete_resume PASSED
tests/test_ats_analyzer.py::test_ats_missing_critical_sections PASSED
tests/test_database.py::test_database_crud_operations PASSED
tests/test_job_analyzer.py::test_empty_and_short_job_description PASSED
tests/test_job_analyzer.py::test_job_description_parsing PASSED
tests/test_job_analyzer.py::test_top_keywords_extraction PASSED
tests/test_matcher.py::test_tfidf_identical_and_unrelated_texts PASSED
tests/test_matcher.py::test_calculate_match_structure_and_formula PASSED
tests/test_pdf_parser.py::test_clean_text_removes_bullets_and_whitespace PASSED
tests/test_pdf_parser.py::test_extract_clean_words PASSED
tests/test_pdf_parser.py::test_extract_contact_info_regex PASSED
tests/test_pdf_parser.py::test_parse_pdf_sample_file PASSED
tests/test_recommendations.py::test_recommend_roles_ranks_python_backend_high PASSED
tests/test_recommendations.py::test_recommend_roles_ranks_ml_high_when_ml_skills_present PASSED
tests/test_recommendations.py::test_generate_improvement_suggestions PASSED
tests/test_skill_extractor.py::test_extract_single_and_multiword_skills PASSED
tests/test_skill_extractor.py::test_skill_aliases_normalization PASSED
tests/test_skill_extractor.py::test_skill_categorization_integrity PASSED
tests/test_skill_extractor.py::test_empty_and_noise_text PASSED

============================= 19 passed in 2.85s =============================
```

---

## 📸 Screenshots & Workflow

*(Add screenshots of your application here before pushing to your GitHub portfolio)*

1. **Dashboard Overview:** Displays overall match score gauge, candidate details, and skill category charts.
2. **Resume Analyzer:** Upload PDF or click "Load Sample Resume" to inspect extracted sections and contact badges.
3. **Job Description:** Paste posting or pick one-click presets to view partitioned required vs preferred skills.
4. **Match Analysis:** Review side-by-side matched skills, missing competencies, and mathematical score explanation.
5. **ATS Audit:** Review section passes, page count warnings, and action verb density.
6. **Career Recommendations:** View ranked suitability for roles like *Python Developer* or *Data Analyst*.
7. **History:** View, inspect, or delete previous analysis sessions.

---

## 🌐 Deployment to Streamlit Community Cloud

1. Create a free account at [share.streamlit.io](https://share.streamlit.io).
2. Connect your GitHub account and select your repository: `ai-resume-analyzer`.
3. Set the Main file path to: `app.py`.
4. Click **Deploy!**

> **Note on SQLite in Cloud Deployments:**  
> Streamlit Community Cloud runs on ephemeral container instances. While SQLite works out-of-the-box for session persistence, changes will reset whenever the cloud container restarts. For permanent production cloud storage, connect to a free hosted PostgreSQL database (such as Supabase or Neon).

---

## 🔒 Security & Privacy Practices

- **Zero Cloud Transmission:** Candidate resume data remains entirely in local RAM / memory. No text is forwarded to external APIs.
- **File Validation:** Uploads are strictly validated for `.pdf` file signatures and limited to 5MB to avoid denial-of-service memory exhausts.
- **SQL Injection Prevention:** Every database query uses parameterized SQL (`?`) rather than f-string string interpolation.
- **Clean Git Tracking:** `.gitignore` excludes local virtual environments, bytecode cache, and SQLite databases.

---

## 💡 Future Enhancements

- [ ] Export PDF / DOCX customized improvement audit reports.
- [ ] Integration with open-source local LLMs (Ollama / LLaMA 3) for contextual bullet-point rewriting.
- [ ] Multi-resume bulk comparison for technical recruiters.
- [ ] Support for LaTeX (`.tex`) resume source files.

---

## 📄 License

This project is licensed under the **MIT License** — open-source and free to use for personal, academic, and portfolio purposes.
