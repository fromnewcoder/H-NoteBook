from docx import Document


def parse_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    doc = Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())
    return "\n".join(paragraphs)
