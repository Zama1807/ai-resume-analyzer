"""
PDF Parser & Resume Ingestion Utility
======================================
Safely extracts text, contact information, metadata, and 
logical sections from PDF resumes using PyMuPDF (fitz).
"""

import re
import pymupdf  # PyMuPDF
from typing import Union, BinaryIO
from utils.text_cleaner import clean_text

# Maximum allowed resume size (5 Megabytes)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# Section Header Signatures for Structured Resume Parsing
SECTION_PATTERNS = {
    "summary": [
        r"\b(?:professional\s+)?summary\b",
        r"\bobjective\b",
        r"\bcareer\s+objective\b",
        r"\bprofile\b",
        r"\babout\s+me\b"
    ],
    "skills": [
        r"\btechnical\s+skills\b",
        r"\bskills\b",
        r"\bcore\s+competencies\b",
        r"\btechnologies\b",
        r"\bprogramming\s+languages\b",
        r"\btools\s+(&|and)\s+technologies\b"
    ],
    "experience": [
        r"\bwork\s+experience\b",
        r"\bprofessional\s+experience\b",
        r"\bexperience\b",
        r"\bemployment\s+history\b",
        r"\binternships?\b",
        r"\bwork\s+history\b"
    ],
    "education": [
        r"\beducation\b",
        r"\bacademics?\b",
        r"\bacademic\s+background\b",
        r"\bqualifications?\b",
        r"\beducational\s+qualifications?\b"
    ],
    "projects": [
        r"\bprojects?\b",
        r"\bacademic\s+projects?\b",
        r"\bpersonal\s+projects?\b",
        r"\bkey\s+projects?\b"
    ],
    "certifications": [
        r"\bcertifications?\b",
        r"\blicenses?\s+(&|and)\s+certifications?\b",
        r"\bcourses?\b",
        r"\bachievements?\b",
        r"\bawards?\b"
    ]
}


def extract_contact_info(text: str) -> dict:
    """
    Extracts Candidate Name, Email, Phone number, and Links (LinkedIn, GitHub)
    using robust regular expressions.
    """
    contact = {
        "name": "Not Detected",
        "email": "Not Detected",
        "phone": "Not Detected",
        "linkedin": "Not Detected",
        "github": "Not Detected"
    }

    if not text:
        return contact

    # 1. Email Extraction
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        contact["email"] = email_match.group(0).strip()

    # 2. Phone Number Extraction (supports International + Country codes, dashes, parentheses)
    phone_match = re.search(r"(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{3,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}", text)
    if phone_match and len(re.sub(r"\D", "", phone_match.group(0))) >= 10:
        contact["phone"] = phone_match.group(0).strip()

    # 3. LinkedIn Profile
    linkedin_match = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group(0).strip()

    # 4. GitHub Profile
    github_match = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if github_match:
        contact["github"] = github_match.group(0).strip()

    # 5. Candidate Name Heuristic:
    # Look at the first 4 non-empty lines before email or phone appear.
    # Exclude lines that look like headers, URLs, or job titles.
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:4]:
        # Skip if contains email, URL, or numbers
        if "@" in line or "http" in line or "www." in line or re.search(r"\d", line):
            continue
        # Skip if it is a common section keyword
        if any(re.search(pat, line, re.IGNORECASE) for pats in SECTION_PATTERNS.values() for pat in pats):
            continue
        # Names are typically 2 to 4 capitalized words, 3 to 35 chars
        words = line.split()
        if 1 <= len(words) <= 4 and 3 <= len(line) <= 35:
            # Check if alphabetic
            clean_line = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            if clean_line:
                contact["name"] = clean_line.title()
                break

    return contact


def extract_sections(text: str) -> dict:
    """
    Segments resume text into logical sections (Education, Experience, Skills, etc.)
    by detecting section header boundaries.
    """
    sections = {key: "" for key in SECTION_PATTERNS.keys()}
    lines = text.split("\n")

    current_section = None
    section_buffers = {key: [] for key in SECTION_PATTERNS.keys()}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if this line is a section header (usually short, <= 40 chars)
        matched_header = None
        if len(stripped) <= 45:
            for sec_name, patterns in SECTION_PATTERNS.items():
                for pat in patterns:
                    if re.match(r"^[\s#*\-_:]*" + pat + r"[\s#*\-_:]*$", stripped, re.IGNORECASE):
                        matched_header = sec_name
                        break
                if matched_header:
                    break

        if matched_header:
            current_section = matched_header
        elif current_section:
            section_buffers[current_section].append(stripped)

    for sec_name, buffer_lines in section_buffers.items():
        sections[sec_name] = "\n".join(buffer_lines).strip()

    return sections


def parse_pdf(file_input: Union[str, bytes, BinaryIO]) -> dict:
    """
    Primary ingestion function for PDF resumes.
    Accepts a filepath, raw bytes, or a Streamlit UploadedFile buffer.
    
    Returns a structured dictionary with raw text, cleaned text,
    contact info, sections, and document metadata.
    """
    result = {
        "success": False,
        "error_message": "",
        "raw_text": "",
        "cleaned_text": "",
        "page_count": 0,
        "word_count": 0,
        "char_count": 0,
        "contact_info": {},
        "sections": {},
        "detected_sections_list": [],
        "is_scanned": False
    }

    try:
        # 1. Read document bytes safely
        if isinstance(file_input, str):
            doc = pymupdf.open(file_input)
        elif isinstance(file_input, bytes):
            if len(file_input) > MAX_FILE_SIZE_BYTES:
                result["error_message"] = "File size exceeds maximum limit of 5MB."
                return result
            doc = pymupdf.open(stream=file_input, filetype="pdf")
        else:
            # File-like object (e.g. Streamlit UploadedFile)
            data = file_input.read()
            if len(data) > MAX_FILE_SIZE_BYTES:
                result["error_message"] = "File size exceeds maximum limit of 5MB."
                return result
            # Reset buffer pointer for safety
            if hasattr(file_input, "seek"):
                file_input.seek(0)
            doc = pymupdf.open(stream=data, filetype="pdf")

        result["page_count"] = len(doc)
        if result["page_count"] == 0:
            result["error_message"] = "The uploaded PDF document contains 0 pages."
            return result

        # 2. Extract text page-by-page
        page_texts = []
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text")
            if page_text:
                page_texts.append(page_text)

        raw_combined = "\n\n".join(page_texts).strip()
        result["raw_text"] = raw_combined

        # 3. Check for Scanned / Image-only PDF
        if len(raw_combined) < 50:
            result["is_scanned"] = True
            result["error_message"] = (
                "Unable to extract text. This appears to be a scanned or image-based PDF. "
                "Please upload a text-based PDF generated from Word, Canva, LaTeX, or Google Docs."
            )
            return result

        # 4. Clean and normalize text
        cleaned = clean_text(raw_combined)
        result["cleaned_text"] = cleaned
        result["char_count"] = len(cleaned)
        result["word_count"] = len(cleaned.split())

        # 5. Extract contact info and logical sections
        result["contact_info"] = extract_contact_info(cleaned)
        result["sections"] = extract_sections(cleaned)
        result["detected_sections_list"] = [
            sec for sec, content in result["sections"].items() if len(content) > 10
        ]

        result["success"] = True

    except Exception as e:
        result["error_message"] = f"Failed to parse PDF document: {str(e)}"

    return result
