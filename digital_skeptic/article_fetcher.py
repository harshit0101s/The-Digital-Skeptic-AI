from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup
from readability import Document  # type: ignore
import trafilatura  # type: ignore

@dataclass
class Article:
    url: Optional[str]
    title: str
    text: str
    html: Optional[str]

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/123.0 Safari/537.36")

def _basic_extract(html: str) -> Tuple[str, str]:
    doc = Document(html)
    title = doc.short_title() or ""
    content_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(content_html, "html.parser")
    # Remove scripts/styles
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return title, text

def fetch_article(url: str) -> Article:
    """Fetch article with fallbacks; raise on network errors."""
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    html = r.text

    # Try trafilatura first (often robust)
    extracted = trafilatura.extract(html, include_comments=False, favor_recall=True)
    if extracted and len(extracted) > 400:
        title = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE|re.DOTALL)
        title_text = title.group(1).strip() if title else ""
        return Article(url=url, title=title_text, text=extracted.strip(), html=html)

    # Fallback to readability
    title, text = _basic_extract(html)
    return Article(url=url, title=title, text=text, html=html)

def read_local_file(path: str) -> Article:
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    title = path.split("/")[-1]
    return Article(url=None, title=title, text=txt.strip(), html=None)
