"""
smoke_test.py
-------------
Verifies the full toolkit WITHOUT hitting real websites (fully mocked) —
run this any time after changing code, or right after cloning the repo.

Usage: python smoke_test.py
"""

from crawler_toolkit.robots_checker import audit_robots_txt, summarize_posture
from crawler_toolkit.llms_txt_validator import validate_llms_txt
from crawler_toolkit.llms_txt_generator import generate_llms_txt


def main():
    checks = 0

    # --- robots.txt auditing ---
    selective_robots = """
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: *
Allow: /
"""
    results = audit_robots_txt(selective_robots)
    posture = summarize_posture(results)
    assert posture["search_retrieval_pct_allowed"] == 100.0, "Expected all search/retrieval bots allowed"
    assert posture["visibility_score"] == 100.0, f"Expected visibility_score 100.0, got {posture['visibility_score']}"
    gptbot_row = next(r for r in results if r["name"] == "GPTBot")
    assert gptbot_row["allowed"] is False, "GPTBot should be blocked"
    print("[PASS] selective robots.txt (block training, allow search/retrieval) scores 100/100 visibility, GPTBot correctly blocked")
    checks += 1

    fully_closed = "User-agent: *\nDisallow: /\n"
    results2 = audit_robots_txt(fully_closed)
    posture2 = summarize_posture(results2)
    assert posture2["visibility_score"] == 0.0, f"Expected 0.0, got {posture2['visibility_score']}"
    assert "Closed" in posture2["posture"]
    print("[PASS] fully-closed robots.txt correctly scores 0/100 and reports 'Closed' posture")
    checks += 1

    empty_robots = ""
    results3 = audit_robots_txt(empty_robots)
    posture3 = summarize_posture(results3)
    assert posture3["visibility_score"] == 100.0
    print("[PASS] empty robots.txt (implicit allow-all) correctly scores 100/100")
    checks += 1

    # --- llms.txt validation ---
    valid_llms = """# IndexCraft

> A technical SEO and AI search publication.

## Guides

- [Technical SEO Hub](https://indexcraft.in/technical-seo-hub): Core guide index

## Optional

- [About](https://indexcraft.in/about)
"""
    result = validate_llms_txt(valid_llms)
    assert result["issues"] == [], f"Expected zero issues, got {result['issues']}"
    print("[PASS] fully valid llms.txt (dash bullets) produces zero issues")
    checks += 1

    asterisk_llms = """# GitHub

> A developer platform.

## Section

* [Link One](https://example.com/one): First link
* [Link Two](https://example.com/two): Second link
"""
    result2 = validate_llms_txt(asterisk_llms)
    assert result2["stats"]["total_links"] == 2, f"Expected 2 links with asterisk bullets, got {result2['stats']['total_links']}"
    assert result2["issues"] == [], f"Expected zero issues on asterisk-bullet file, got {result2['issues']}"
    print("[PASS] llms.txt using asterisk bullets (real-world variant) parses correctly — regression guard for the bullet-marker bug")
    checks += 1

    missing_h1 = "> Summary with no title\n\n## Section\n- [link](https://example.com)\n"
    result3 = validate_llms_txt(missing_h1)
    errors = [i for i in result3["issues"] if i["severity"] == "error"]
    assert len(errors) == 1 and "H1" in errors[0]["message"]
    print("[PASS] missing H1 correctly flagged as an error")
    checks += 1

    relative_and_dup = """# Test

## Section

- [Page A](/relative-path)
- [Page B](https://example.com/dup)
- [Page C](https://example.com/dup)
"""
    result4 = validate_llms_txt(relative_and_dup)
    messages = [i["message"] for i in result4["issues"]]
    assert any("relative" in m for m in messages), "Expected a relative-URL warning"
    assert any("Duplicate URL" in m for m in messages), "Expected a duplicate-URL warning"
    print("[PASS] relative URLs and duplicate URLs both correctly flagged")
    checks += 1

    # --- llms.txt generation + round-trip validation ---
    urls = [
        "https://indexcraft.in/",
        "https://indexcraft.in/blog/geo-basics",
        "https://indexcraft.in/guides/technical-seo-hub",
    ]
    metadata = {
        "https://indexcraft.in/": {"title": "IndexCraft", "description": "Homepage"},
        "https://indexcraft.in/blog/geo-basics": {"title": "GEO Basics", "description": "Intro to GEO"},
        "https://indexcraft.in/guides/technical-seo-hub": {"title": "Technical SEO Hub", "description": ""},
    }
    generated = generate_llms_txt("IndexCraft", "A technical SEO and AI search publication.", urls, metadata)
    round_trip = validate_llms_txt(generated)
    assert round_trip["issues"] == [], f"Generator output should be self-valid, got {round_trip['issues']}"
    assert round_trip["stats"]["total_links"] == 3
    print("[PASS] generated llms.txt round-trips through the validator with zero issues")
    checks += 1

    print(f"\n=== ALL {checks} CHECKS PASSED ===")
    print("Verified: robots.txt scoring across open/closed/selective configs,")
    print("llms.txt validation (both bullet styles, structural errors), and")
    print("generator output round-tripping cleanly through the validator.")
    print("\nNote: live network fetching (fetch_robots_txt, fetch_sitemap_urls,")
    print("fetch_page_metadata, check_llms_txt_exists) was verified separately")
    print("against real domains during development — this smoke test covers")
    print("the pure logic so it can run offline, in CI, or right after cloning.")


if __name__ == "__main__":
    main()
