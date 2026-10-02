"""
Text Cleaning & Normalization Utility
======================================
Cleans raw text extracted from resumes and job descriptions.
Removes special formatting artifacts, standardizes whitespace,
and extracts clean normalized tokens.
"""

import re
import unicodedata

def clean_text(raw_text: str) -> str:
    """
    Cleans raw text extracted from documents:
    - Normalizes unicode characters
    - Replaces bullet points and symbols with standard separators
    - Removes unprintable characters
    - Normalizes multi-spaces and newlines
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    # 1. Normalize unicode characters (e.g., convert fancy quotes or ligatures)
    text = unicodedata.normalize("NFKD", raw_text)

    # 2. Standardize bullet points and list markers to a simple dash
    bullet_pattern = r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF\u25CB\u25A0\u25BA\u25C6\u27A2\u2714\u2713•▪►*]"
    text = re.sub(bullet_pattern, "\n- ", text)

    # 3. Replace non-breaking spaces and tabs with standard space
    text = text.replace("\xa0", " ").replace("\t", " ")

    # 4. Remove excessive line breaks (more than 2 consecutive newlines -> 2 newlines)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # 5. Remove excessive horizontal whitespace within lines
    lines = [re.sub(r"[ ]{2,}", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line)

    return text.strip()


def extract_clean_words(text: str) -> list[str]:
    """
    Splits text into lowercase tokens preserving tech keywords like C++, C#, .NET.
    """
    if not text:
        return []
    # Tokenize words, including special tech suffixes like ++ or # or .net
    raw_tokens = re.findall(r"[a-zA-Z0-9+#.-]+", text.lower())
    clean_tokens = []
    for t in raw_tokens:
        t_clean = t.strip(".,;:()![]{}'\"")
        if len(t_clean) >= 1:
            clean_tokens.append(t_clean)
    return clean_tokens
