import chardet


def parse_txt(content: bytes) -> str:
    """Detect encoding and decode text content."""
    result = chardet.detect(content)
    encoding = result.get("encoding", "utf-8") or "utf-8"
    return content.decode(encoding, errors="replace")
