# AI Crawler Access Toolkit

Three tools in one, for the AI-search-visibility side of technical SEO:

1. **`audit`** — checks your `robots.txt` against 24 known AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, and more), tells you which ones can actually reach your content, and gives you an **AI Visibility Score** — because blocking a *training* crawler and blocking a *search/retrieval* crawler are very different decisions with very different consequences, and most robots.txt audits don't distinguish between them.
2. **`validate-llms`** — checks an existing `llms.txt` file against the community spec.
3. **`generate-llms`** — drafts a `llms.txt` from your sitemap automatically.

## Why this exists

`llms.txt` is a young, informally-governed standard (proposed by Jeremy Howard, see [llmstxt.org](https://llmstxt.org)) for telling AI tools what your site is and what to read first. Adoption is still early — most sites don't have one yet, and most robots.txt files were written for Googlebot, not for the 20+ AI-specific crawlers that now determine whether your brand shows up in ChatGPT, Claude, Perplexity, and Gemini answers.

The distinction this toolkit is built around: **blocking a training crawler (GPTBot, ClaudeBot) has no effect on citations today** — models already trained aren't retroactively affected, and it's a data-licensing decision, not a visibility one. **Blocking a search/retrieval crawler (OAI-SearchBot, Claude-SearchBot, PerplexityBot) has an immediate effect** — you disappear from that platform's answers within hours. Most tools and guides conflate these. This one doesn't.

---

## 1. What you need

- **Python 3.10+**
- No API keys — this only reads public `robots.txt` / `llms.txt` files and page HTML.

```bash
python3 --version
```

---

## 2. Setup

```bash
cd ai-crawler-access-toolkit
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. Usage

### Audit a domain's AI crawler access

```bash
python run_toolkit.py audit --domain https://indexcraft.in
```

Fetches `robots.txt`, checks it against every bot in the database, checks whether `llms.txt` exists, and writes a CSV + Markdown report to `reports/`. The Markdown report is meant to be pasted straight into a Slack message or client deliverable — it includes a plain-language "what to fix" section, not just raw data.

### Validate an existing llms.txt

```bash
python run_toolkit.py validate-llms --file llms.txt
# or, for a hosted file:
python run_toolkit.py validate-llms --url https://indexcraft.in/llms.txt
```

### Generate a draft llms.txt from your sitemap

```bash
python run_toolkit.py generate-llms \
  --sitemap https://indexcraft.in/sitemap.xml \
  --name "IndexCraft" \
  --summary "A technical SEO and AI search publication." \
  --output llms.txt
```

Fetches every page in the sitemap, pulls the `<title>` and meta description, and groups pages into sections by URL path (`/blog/...` → a "Blog" section, etc). **This is a draft** — auto-grouping by path is a reasonable starting heuristic, not a substitute for reviewing the output.

Use `--urls` instead of/alongside `--sitemap` to include specific pages, `--max-urls` to cap how many pages get fetched, and `--skip-fetch-metadata` to generate faster without pulling titles/descriptions (you'll get the raw URL as the title instead).

---

## 4. Verifying it works

```bash
python smoke_test.py
```

Runs 8 checks covering robots.txt scoring (open / closed / selective configurations), llms.txt validation (including a regression guard for a real bug found during development — see below), and generator output round-tripping cleanly through the validator. No real network calls, safe to run anytime.

---

## 5. Reading the bot database

`crawler_toolkit/bot_database.py` is the part of this repo worth reading even if you never run the code — 24 AI crawlers, each tagged with:

- **category**: `training` / `search_retrieval` / `on_demand` / `opt_out_token`
- **respects_robots_txt**: `yes` / `no` / `unclear`, per vendor documentation (e.g. Perplexity explicitly states `Perplexity-User` does *not* obey robots.txt for on-demand fetches)
- **source**: where that claim comes from

This list changes a few times a year as vendors ship new bots — update this file when they do. See `sample_output/access_audit_example.md` for what a real audit report (run against github.com) looks like.

---

## 6. What "AI Visibility Score" actually measures

The score weights **search/retrieval bots (70%)** and **on-demand bots (30%)** — the ones that affect whether you're cited *right now*. Training-bot access is reported separately and isn't counted toward the score, because allowing or blocking GPTBot/ClaudeBot training is a strategic IP decision, not a visibility lever — it doesn't change whether you show up in today's answers.

| Score | Posture |
|---|---|
| 90–100 | Open — visible across nearly all AI search/retrieval bots |
| 50–89 | Selective — some blocked, partial visibility |
| 0–49 | Closed — likely invisible in AI answers |

---

## 7. A real bug this tool caught during its own development

While testing the validator against GitHub's real, production `llms.txt` file, it initially misreported 117 real links as "sections with no links." The cause: the llms.txt spec doesn't mandate a bullet character, and GitHub's file uses `*` while the examples on llmstxt.org use `-`. The validator only accepted `-`. Fixed to accept both, with a permanent regression test (`smoke_test.py`) covering the asterisk case — this is exactly the kind of gap that only shows up against real-world files, not hand-written test fixtures, which is why this toolkit was validated against a live, production llms.txt rather than only synthetic examples.

---

## Project structure

```
ai-crawler-access-toolkit/
├── run_toolkit.py                 # CLI entry point (audit / validate-llms / generate-llms)
├── smoke_test.py                   # 8 automated checks, no real network calls
├── requirements.txt
├── crawler_toolkit/
│   ├── bot_database.py              # the 24-crawler reference database
│   ├── robots_checker.py            # robots.txt parsing + scoring
│   ├── llms_txt_validator.py        # spec compliance checks
│   ├── llms_txt_generator.py        # sitemap → draft llms.txt
│   ├── sitemap.py                    # shared sitemap.xml parsing
│   └── report.py                     # CSV + Markdown report writers
├── reports/                        # your audit outputs land here
└── sample_output/                  # example reports, incl. a real GitHub llms.txt
```

---
