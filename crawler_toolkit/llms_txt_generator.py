"""
llms_txt_generator.py
-----------------------
Generates a DRAFT llms.txt from a sitemap: fetches each page, pulls the
<title> and meta description, and groups pages into sections by URL path
(e.g. everything under /blog/ becomes a "Blog" section).

This is a starting point, not a finished file — always review the output
before publishing. Auto-grouping by path is a reasonable heuristic but
won't match every site's information architecture perfectly.
"""

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def fetch_page_metadata(url: str, timeout: int = 15) -> dict:
    """Returns {title, description} for a URL, best-effort (empty strings on failure)."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "AICrawlerAccessToolkit/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else url
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"].strip()

        return {"title": title, "description": description}
    except Exception:
        return {"title": url, "description": ""}


def _section_name_for_url(url: str) -> str:
    """Heuristic: first meaningful path segment becomes the section name."""
    path = urlparse(url).path.strip("/")
    if not path:
        return "Pages"
    segment = path.split("/")[0]
    return segment.replace("-", " ").replace("_", " ").title()


def generate_llms_txt(site_name: str, site_summary: str, urls: list, page_metadata: dict = None) -> str:
    """
    urls: list of URL strings
    page_metadata: optional dict of {url: {title, description}} — if not
                   provided for a URL, generate_llms_txt will just use the
                   URL itself as the title (no network calls made here;
                   fetching is the caller's job via fetch_page_metadata).
    """
    page_metadata = page_metadata or {}

    sections = {}
    for url in urls:
        section_name = _section_name_for_url(url)
        sections.setdefault(section_name, []).append(url)

    lines = [f"# {site_name}", ""]
    if site_summary:
        lines.append(f"> {site_summary}")
        lines.append("")

    ordered_sections = sorted(sections.keys(), key=lambda s: (s != "Pages", s))

    for section_name in ordered_sections:
        lines.append(f"## {section_name}")
        lines.append("")
        for url in sections[section_name]:
            meta = page_metadata.get(url, {"title": url, "description": ""})
            title = meta.get("title") or url
            description = meta.get("description", "")
            if description:
                lines.append(f"- [{title}]({url}): {description}")
            else:
                lines.append(f"- [{title}]({url})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
