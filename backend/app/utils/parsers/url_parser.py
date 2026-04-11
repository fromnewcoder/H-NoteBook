import ssl

import httpx
from bs4 import BeautifulSoup


async def parse_url(url: str) -> str:
    """Fetch URL and extract plain text content."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with httpx.AsyncClient(timeout=30.0, verify=ssl_context) as client:
        response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Get text and clean up whitespace
        text = soup.get_text(separator="\n", strip=True)
        # Remove excessive blank lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

