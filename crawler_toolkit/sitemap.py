"""
sitemap.py
----------
Small shared helper: parses a sitemap.xml (including sitemap-index files,
one level deep) and returns a flat list of page URLs.
"""

import requests
from bs4 import BeautifulSoup


def fetch_sitemap_urls(sitemap_url: str, timeout: int = 20) -> list:
    resp = requests.get(sitemap_url, timeout=timeout, headers={"User-Agent": "AICrawlerAccessToolkit/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "xml")

    sub_sitemaps = [loc.text.strip() for loc in soup.select("sitemap > loc")]
    if sub_sitemaps:
        urls = []
        for sub in sub_sitemaps:
            urls.extend(fetch_sitemap_urls(sub, timeout=timeout))
        return urls

    return [loc.text.strip() for loc in soup.select("url > loc")]
