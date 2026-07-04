"""
report.py
---------
Writes the access-audit results to:
  - access_audit_TIMESTAMP.csv     : one row per bot (name, category, allowed, etc.)
  - access_audit_TIMESTAMP.md      : human-readable summary with the posture
                                      score, a table, and plain-language
                                      recommendations — this is the file
                                      worth pasting into a Slack message or
                                      client report.
"""

import csv


def write_audit_csv(path: str, audit_results: list):
    fieldnames = ["name", "operator", "category", "allowed", "respects_robots_txt", "purpose"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in audit_results:
            writer.writerow(row)


def write_audit_markdown(path: str, domain: str, audit_results: list, posture: dict, llms_txt_status: dict):
    lines = []
    lines.append(f"# AI Crawler Access Report — {domain}")
    lines.append("")
    lines.append(f"**AI Visibility Score:** {posture['visibility_score']}/100")
    lines.append(f"**Posture:** {posture['posture']}")
    lines.append("")
    lines.append(f"- Search/retrieval bots allowed: {posture['search_retrieval_pct_allowed']}%")
    lines.append(f"- On-demand fetch bots allowed: {posture['on_demand_pct_allowed']}%")
    lines.append(f"- Training bots allowed: {posture['training_pct_allowed']}% (strategic choice, not a visibility factor)")
    lines.append("")

    llms_line = f"**llms.txt:** {'Found at ' + llms_txt_status['url'] if llms_txt_status['exists'] else 'Not found'}"
    lines.append(llms_line)
    lines.append("")

    lines.append("## Bot-by-bot breakdown")
    lines.append("")
    lines.append("| Bot | Operator | Category | Allowed | Respects robots.txt |")
    lines.append("|---|---|---|---|---|")
    for row in audit_results:
        status = "✅ Allowed" if row["allowed"] else "🚫 Blocked"
        lines.append(f"| {row['name']} | {row['operator']} | {row['category']} | {status} | {row['respects_robots_txt']} |")
    lines.append("")

    blocked_retrieval = [r for r in audit_results if r["category"] == "search_retrieval" and not r["allowed"]]
    if blocked_retrieval:
        lines.append("## Action items")
        lines.append("")
        lines.append("These search/retrieval bots are currently blocked — unblocking them has an immediate effect on AI-answer citation eligibility:")
        lines.append("")
        for bot in blocked_retrieval:
            lines.append(f"- **{bot['name']}** ({bot['operator']}) — {bot['purpose']}")
        lines.append("")

    if not llms_txt_status["exists"]:
        lines.append("Consider adding an `llms.txt` file at your domain root — use `generate-llms` in this toolkit to draft one from your sitemap.")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
