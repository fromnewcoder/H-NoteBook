from markdown_it import MarkdownIt


def parse_md(content: str) -> str:
    """Parse markdown and extract plain text."""
    md = MarkdownIt()
    tokens = md.parse(content)
    # Extract plain text from tokens
    text_parts = []
    for token in tokens:
        if token.content:
            text_parts.append(token.content)
        if token.children:
            for child in token.children:
                if child.content:
                    text_parts.append(child.content)
    return "\n".join(text_parts)
