import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# Chunking Configuration
# ============================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size= 700,
    chunk_overlap = 120,
    seperators=["\n\n", "\n", ".", " "]
)


# ============================================================
# Text Cleaning
# ============================================================
def clean_text(text:str)->str:
    """
    Normalize extracted PDF/OCR text.
    """

    text = re.sub(r"\r\n?", "\n", text)

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ============================================================
# Detect Domain-Specific Code Boundaries
# ============================================================

def get_regex_pattern(document_type:str)-> str 

# ============================================================
# Regex-Based Logical Chunking
# ============================================================


# ============================================================
# Create Chunks
# ============================================================