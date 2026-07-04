"""
llms_txt_validator.py
----------------------
Validates a llms.txt file against the community spec (llmstxt.org):

    # Project or Site Name

    > Optional one-line summary in a blockquote.

    Optional free-text paragraphs with extra context.

    ## Section Name

    - [Link title](https://example.com/page): optional one-line note
    - [Another link](https://example.com/page2)

    ## Optional

    - [Lower-priority link](https://example.com/page3)

The spec is intentionally loose — this validator checks the structural
rules that are actually load-bearing (an H1 must exist, links must be
real markdown links, URLs should be absolute) and treats the rest as
style guidance (warnings, not errors).
"""

import re

LINK_LINE_RE = re.compile(r"^[-*]\s*\[([^\]]+)\]\(([^)]+)\)\s*(:\s*(.*))?$")
H1_RE = re.compile(r"^#\s+(.+)$")
H2_RE = re.compile(r"^##\s+(.+)$")
BLOCKQUOTE_RE = re.compile(r"^>\s*(.+)$")


def validate_llms_txt(content: str) -> dict:
    """
    Returns {issues: [...], stats: {...}} where each issue is
    {severity, line, message}.
    """
    lines = content.splitlines()
    issues = []

    h1_found = False
    h1_line_number = None
    blockquote_found = False
    sections = []  # list of {name, line, links: [...]}
    current_section = None
    seen_urls = {}

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()

        h1_match = H1_RE.match(line)
        if h1_match:
            if h1_found:
                issues.append({"severity": "warning", "line": i, "message": "Multiple H1 headings found — llms.txt should have exactly one title at the top."})
            else:
                h1_found = True
                h1_line_number = i
            continue

        h2_match = H2_RE.match(line)
        if h2_match:
            current_section = {"name": h2_match.group(1).strip(), "line": i, "links": []}
            sections.append(current_section)
            continue

        blockquote_match = BLOCKQUOTE_RE.match(line)
        if blockquote_match and not blockquote_found and h1_found and current_section is None:
            blockquote_found = True
            continue

        link_match = LINK_LINE_RE.match(line.strip())
        if link_match:
            title, url = link_match.group(1), link_match.group(2)
            if current_section is None:
                issues.append({"severity": "warning", "line": i, "message": f"Link '{title}' appears before any ## section heading — it won't be grouped with a topic."})
            else:
                current_section["links"].append({"title": title, "url": url, "line": i})

            if not url.startswith(("http://", "https://")):
                issues.append({"severity": "warning", "line": i, "message": f"Link '{title}' uses a relative or non-absolute URL ({url}) — llms.txt consumers may not resolve it correctly."})

            if url in seen_urls:
                issues.append({"severity": "warning", "line": i, "message": f"Duplicate URL also linked on line {seen_urls[url]}: {url}"})
            else:
                seen_urls[url] = i

    if not h1_found:
        issues.append({"severity": "error", "line": 1, "message": "No H1 title found. llms.txt must start with a single '# Title' line."})

    if h1_found and not blockquote_found:
        issues.append({"severity": "warning", "line": h1_line_number or 1, "message": "No blockquote summary ('> ...') found right after the H1 — recommended by the spec to give consumers a one-line description."})

    if not sections:
        issues.append({"severity": "warning", "line": len(lines), "message": "No '##' sections found — llms.txt typically groups links under topic headings."})

    empty_sections = [s for s in sections if not s["links"]]
    for s in empty_sections:
        issues.append({"severity": "warning", "line": s["line"], "message": f"Section '{s['name']}' has no links under it."})

    total_links = sum(len(s["links"]) for s in sections)

    stats = {
        "has_h1": h1_found,
        "has_summary_blockquote": blockquote_found,
        "section_count": len(sections),
        "total_links": total_links,
        "sections": [{"name": s["name"], "link_count": len(s["links"])} for s in sections],
    }

    return {"issues": issues, "stats": stats}
