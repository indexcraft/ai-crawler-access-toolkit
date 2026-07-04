"""
robots_checker.py
------------------
Fetches a domain's robots.txt and checks it against every bot in
bot_database.py, using Python's own urllib.robotparser — the same
group-matching / longest-match logic real crawlers use — instead of
hand-rolled regex. (Regex-based robots.txt parsing is a well-known source
of subtle bugs: multi-agent groups, comments, and precedence rules are
easy to get wrong by hand.)
"""

import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

from crawler_toolkit.bot_database import AI_CRAWLERS


def fetch_robots_txt(domain: str, timeout: int = 20) -> str:
    """domain should be like 'https://indexcraft.in' (no trailing slash needed)."""
    url = urljoin(domain.rstrip("/") + "/", "robots.txt")
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "AICrawlerAccessToolkit/1.0"})
    resp.raise_for_status()
    return resp.text


def check_llms_txt_exists(domain: str, timeout: int = 20) -> dict:
    """Checks for the presence of /llms.txt at the domain root."""
    url = urljoin(domain.rstrip("/") + "/", "llms.txt")
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "AICrawlerAccessToolkit/1.0"})
        return {"exists": resp.status_code == 200, "url": url, "status_code": resp.status_code}
    except requests.RequestException as e:
        return {"exists": False, "url": url, "status_code": None, "error": str(e)}


def audit_robots_txt(robots_txt_text: str, path: str = "/") -> list:
    """
    Returns a list of dicts, one per bot in the database:
        {name, operator, category, allowed, respects_robots_txt, purpose}
    """
    parser = RobotFileParser()
    parser.parse(robots_txt_text.splitlines())

    results = []
    for bot in AI_CRAWLERS:
        allowed = parser.can_fetch(bot["name"], path)
        results.append({
            "name": bot["name"],
            "operator": bot["operator"],
            "category": bot["category"],
            "allowed": allowed,
            "respects_robots_txt": bot["respects_robots_txt"],
            "purpose": bot["purpose"],
        })
    return results


def summarize_posture(audit_results: list) -> dict:
    """
    Produces the headline numbers:
      - search_retrieval bots allowed (the ones that matter most for being
        cited RIGHT NOW — blocking these has an immediate effect)
      - training bots allowed (a strategic/IP choice, not a visibility one)
      - an overall visibility_score out of 100 weighted toward retrieval bots
    """
    def pct_allowed(category):
        rows = [r for r in audit_results if r["category"] == category]
        if not rows:
            return None
        allowed = sum(1 for r in rows if r["allowed"])
        return round((allowed / len(rows)) * 100, 1)

    retrieval_pct = pct_allowed("search_retrieval") or 0
    on_demand_pct = pct_allowed("on_demand") or 0
    training_pct = pct_allowed("training") or 0
    token_pct = pct_allowed("opt_out_token") or 0

    # Visibility score weights retrieval + on-demand heavily since those
    # drive whether you show up in AI answers TODAY. Training access is
    # a separate strategic decision and isn't counted toward this score.
    visibility_score = round((retrieval_pct * 0.7) + (on_demand_pct * 0.3), 1)

    if visibility_score >= 90:
        posture = "Open — visible across nearly all AI search/retrieval bots"
    elif visibility_score >= 50:
        posture = "Selective — some AI search bots blocked, partial visibility"
    else:
        posture = "Closed — most AI search/retrieval bots blocked, likely invisible in AI answers"

    return {
        "visibility_score": visibility_score,
        "posture": posture,
        "search_retrieval_pct_allowed": retrieval_pct,
        "on_demand_pct_allowed": on_demand_pct,
        "training_pct_allowed": training_pct,
        "opt_out_tokens_pct_allowed": token_pct,
    }
