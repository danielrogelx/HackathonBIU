"""
Document Parser — extracts clean text from .txt, .docx, and .pdf files.
Accepts both Streamlit UploadedFile objects and local file paths.
"""

import io
from pathlib import Path


def extract_text(file_source) -> str:
    """
    Extract plain text from a .txt, .docx, or .pdf file.

    Args:
        file_source: Streamlit UploadedFile OR a local file path (str / Path)

    Returns:
        Extracted text as a string
    """
    if hasattr(file_source, "name") and hasattr(file_source, "read"):
        name = file_source.name.lower()
        data = file_source.read()
        file_source.seek(0)
    else:
        path = Path(file_source)
        name = path.name.lower()
        with open(path, "rb") as f:
            data = f.read()

    if name.endswith(".txt"):
        return _decode_hebrew(data)
    elif name.endswith(".docx"):
        return _extract_docx(data)
    elif name.endswith(".pdf"):
        return _extract_pdf(data)
    else:
        raise ValueError(f"Unsupported file type: {name}. Supported: .txt, .docx, .pdf")


def _decode_hebrew(data: bytes) -> str:
    for enc in ["utf-8", "utf-16", "windows-1255", "iso-8859-8"]:
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, Exception):
            continue
    return data.decode("utf-8", errors="replace")


def _extract_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_pdf(data: bytes) -> str:
    import pdfplumber
    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)
