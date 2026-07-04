#!/usr/bin/env python3
"""
AI Crawler Access Toolkit — CLI entry point.

Three subcommands:

  python run_toolkit.py audit --domain https://indexcraft.in
      Fetches robots.txt, checks it against 20+ known AI crawlers, checks
      for llms.txt, and writes a CSV + Markdown report to reports/.

  python run_toolkit.py validate-llms --file llms.txt
      Validates an existing llms.txt file against the community spec.
      Use --url instead of --file to validate one hosted online.

  python run_toolkit.py generate-llms --sitemap https://indexcraft.in/sitemap.xml --name "IndexCraft" --summary "A technical SEO and AI search publication."
      Drafts a llms.txt from your sitemap. Review before publishing —
      this is a starting point, not a finished file.
"""

import argparse
import os
import sys
from datetime import datetime

from crawler_toolkit.robots_checker import fetch_robots_txt, audit_robots_txt, summarize_posture, check_llms_txt_exists
from crawler_toolkit.report import write_audit_csv, write_audit_markdown
from crawler_toolkit.llms_txt_validator import validate_llms_txt
from crawler_toolkit.llms_txt_generator import generate_llms_txt, fetch_page_metadata
from crawler_toolkit.sitemap import fetch_sitemap_urls


def cmd_audit(args):
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"[fetch] {args.domain}/robots.txt")
    try:
        robots_text = fetch_robots_txt(args.domain)
    except Exception as e:
        print(f"[error] could not fetch robots.txt: {e}")
        sys.exit(1)

    audit_results = audit_robots_txt(robots_text)
    posture = summarize_posture(audit_results)
    llms_status = check_llms_txt_exists(args.domain)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(args.output_dir, f"access_audit_{timestamp}.csv")
    md_path = os.path.join(args.output_dir, f"access_audit_{timestamp}.md")

    write_audit_csv(csv_path, audit_results)
    write_audit_markdown(md_path, args.domain, audit_results, posture, llms_status)

    print(f"\n=== DONE ===")
    print(f"AI Visibility Score: {posture['visibility_score']}/100")
    print(f"Posture: {posture['posture']}")
    print(f"llms.txt: {'found' if llms_status['exists'] else 'not found'}")
    print(f"CSV report:      {csv_path}")
    print(f"Markdown report: {md_path}")


def cmd_validate_llms(args):
    if args.url:
        import requests
        print(f"[fetch] {args.url}")
        resp = requests.get(args.url, timeout=20)
        resp.raise_for_status()
        content = resp.text
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        print("[error] provide either --file or --url")
        sys.exit(1)

    result = validate_llms_txt(content)
    errors = [i for i in result["issues"] if i["severity"] == "error"]
    warnings = [i for i in result["issues"] if i["severity"] == "warning"]

    print(f"\n=== VALIDATION RESULT ===")
    print(f"H1 title found:        {result['stats']['has_h1']}")
    print(f"Summary blockquote:    {result['stats']['has_summary_blockquote']}")
    print(f"Sections found:        {result['stats']['section_count']}")
    print(f"Total links:           {result['stats']['total_links']}")
    print(f"Errors:                {len(errors)}")
    print(f"Warnings:              {len(warnings)}")

    if result["issues"]:
        print("\n--- Issues ---")
        for issue in result["issues"]:
            print(f"[{issue['severity'].upper()}] line {issue['line']}: {issue['message']}")
    else:
        print("\nNo issues found — this llms.txt is fully spec-compliant.")


def cmd_generate_llms(args):
    urls = list(args.urls) if args.urls else []
    if args.sitemap:
        print(f"[sitemap] discovering URLs from {args.sitemap}")
        sitemap_urls = fetch_sitemap_urls(args.sitemap)
        urls.extend(u for u in sitemap_urls if u not in urls)
        print(f"[sitemap] found {len(sitemap_urls)} URLs")

    if args.max_urls and len(urls) > args.max_urls:
        print(f"[cap] capping to first {args.max_urls} URLs")
        urls = urls[: args.max_urls]

    page_metadata = {}
    if not args.skip_fetch_metadata:
        for url in urls:
            print(f"[fetch] {url}")
            page_metadata[url] = fetch_page_metadata(url)

    content = generate_llms_txt(args.name, args.summary, urls, page_metadata)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n=== DONE ===")
    print(f"Draft written to: {args.output}")
    print(f"{len(urls)} pages included across sections.")
    print("Review and edit before publishing — this is a starting draft, not a final file.")


def main():
    parser = argparse.ArgumentParser(description="AI Crawler Access Toolkit — robots.txt AI-bot audit + llms.txt tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_audit = subparsers.add_parser("audit", help="Audit a domain's robots.txt against known AI crawlers")
    p_audit.add_argument("--domain", required=True, help="e.g. https://indexcraft.in")
    p_audit.add_argument("--output-dir", default="reports")
    p_audit.set_defaults(func=cmd_audit)

    p_validate = subparsers.add_parser("validate-llms", help="Validate an existing llms.txt file")
    p_validate.add_argument("--file", help="Path to a local llms.txt file")
    p_validate.add_argument("--url", help="URL of a hosted llms.txt file")
    p_validate.set_defaults(func=cmd_validate_llms)

    p_generate = subparsers.add_parser("generate-llms", help="Generate a draft llms.txt from a sitemap")
    p_generate.add_argument("--sitemap", help="Sitemap URL to discover pages from")
    p_generate.add_argument("--urls", nargs="*", help="Explicit URLs to include (in addition to sitemap, if given)")
    p_generate.add_argument("--name", required=True, help="Site/project name for the H1 title")
    p_generate.add_argument("--summary", default="", help="One-line summary for the blockquote")
    p_generate.add_argument("--output", default="llms.txt")
    p_generate.add_argument("--max-urls", type=int, default=50)
    p_generate.add_argument("--skip-fetch-metadata", action="store_true", help="Don't fetch each page's title/description (faster, but titles will just be the URL)")
    p_generate.set_defaults(func=cmd_generate_llms)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
