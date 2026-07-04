"""
bot_database.py
----------------
A maintained reference of AI crawler / agent user-agent strings, current as
of mid-2026. This is the single most valuable file in this repo — keeping
it accurate and up to date is what makes the audit trustworthy.

Categories:
  - "training"          : bulk crawl used to train future model versions.
                           Blocking has NO retroactive effect on data already
                           collected, and no immediate effect on citations.
  - "search_retrieval"  : periodic indexing used to power citations/answers
                           in that platform's AI search product. Blocking
                           has an IMMEDIATE effect on whether you can be
                           cited — this is the category that matters most
                           for AI visibility today.
  - "on_demand"         : fetches a specific page only when a user pastes/
                           references that URL in a live chat session.
  - "opt_out_token"     : not a real crawler — a robots.txt-only token that
                           controls whether a company's other systems (which
                           already have your content via normal search
                           indexing) may use it for AI training.

respects_robots_txt: "yes" | "no" | "unclear" — per vendor statements and
third-party audits current as of mid-2026. Re-verify periodically; this is
exactly the kind of thing that changes without much announcement.

Update this file whenever a vendor publishes a new bot or changes stated
behavior — that's the whole point of keeping it as one clean data file
instead of scattered across code.
"""

AI_CRAWLERS = [
    # ---------------- OpenAI ----------------
    {
        "name": "GPTBot",
        "operator": "OpenAI",
        "category": "training",
        "purpose": "Crawls public pages to build training data for future models.",
        "respects_robots_txt": "yes",
        "source": "platform.openai.com/docs/bots",
    },
    {
        "name": "OAI-SearchBot",
        "operator": "OpenAI",
        "category": "search_retrieval",
        "purpose": "Builds the index that powers ChatGPT Search citations.",
        "respects_robots_txt": "yes",
        "source": "platform.openai.com/docs/bots",
    },
    {
        "name": "ChatGPT-User",
        "operator": "OpenAI",
        "category": "on_demand",
        "purpose": "Fetches a page live when a user asks ChatGPT about a specific URL.",
        "respects_robots_txt": "yes",
        "source": "platform.openai.com/docs/bots",
    },

    # ---------------- Anthropic ----------------
    {
        "name": "ClaudeBot",
        "operator": "Anthropic",
        "category": "training",
        "purpose": "Anthropic's primary crawler for foundation model training.",
        "respects_robots_txt": "yes",
        "source": "support.anthropic.com (crawler article)",
    },
    {
        "name": "anthropic-ai",
        "operator": "Anthropic",
        "category": "training",
        "purpose": "Secondary training-data user agent observed alongside ClaudeBot.",
        "respects_robots_txt": "yes",
        "source": "support.anthropic.com (crawler article)",
    },
    {
        "name": "Claude-SearchBot",
        "operator": "Anthropic",
        "category": "search_retrieval",
        "purpose": "Search-time retrieval, independently controllable from ClaudeBot training.",
        "respects_robots_txt": "yes",
        "source": "support.anthropic.com (crawler article)",
    },
    {
        "name": "Claude-User",
        "operator": "Anthropic",
        "category": "on_demand",
        "purpose": "Fetches a page live when a user references a URL in a Claude conversation.",
        "respects_robots_txt": "yes",
        "source": "support.anthropic.com (crawler article)",
    },

    # ---------------- Perplexity ----------------
    {
        "name": "PerplexityBot",
        "operator": "Perplexity",
        "category": "search_retrieval",
        "purpose": "Periodic indexing that builds Perplexity's citation source pool.",
        "respects_robots_txt": "yes",
        "source": "docs.perplexity.ai/guides/bots",
    },
    {
        "name": "Perplexity-User",
        "operator": "Perplexity",
        "category": "on_demand",
        "purpose": "Real-time fetch triggered by a specific user question.",
        "respects_robots_txt": "no",
        "source": "docs.perplexity.ai/guides/bots — vendor documents this bot does not obey robots.txt for on-demand fetches",
    },

    # ---------------- Google ----------------
    {
        "name": "Googlebot",
        "operator": "Google",
        "category": "search_retrieval",
        "purpose": "Standard Search crawler — also powers AI Overviews via the same index. Blocking removes you from Google Search entirely, not just AI Overviews.",
        "respects_robots_txt": "yes",
        "source": "developers.google.com/search/docs/crawling-indexing/googlebot",
    },
    {
        "name": "Google-Extended",
        "operator": "Google",
        "category": "opt_out_token",
        "purpose": "Not a crawler — a robots.txt token that opts your content out of Gemini/Vertex AI training. Does not affect Google Search ranking.",
        "respects_robots_txt": "yes",
        "source": "developers.google.com/search/docs/crawling-indexing/google-common-crawlers",
    },
    {
        "name": "GoogleOther",
        "operator": "Google",
        "category": "training",
        "purpose": "Internal Google R&D and product-team crawls outside core Search/Ads.",
        "respects_robots_txt": "yes",
        "source": "developers.google.com/search/docs/crawling-indexing/google-common-crawlers",
    },

    # ---------------- Microsoft ----------------
    {
        "name": "Bingbot",
        "operator": "Microsoft",
        "category": "search_retrieval",
        "purpose": "Standard Bing crawler — also feeds Copilot's answer sourcing.",
        "respects_robots_txt": "yes",
        "source": "www.bing.com/webmasters/help/which-crawlers-does-bing-use",
    },

    # ---------------- Amazon ----------------
    {
        "name": "Amazonbot",
        "operator": "Amazon",
        "category": "training",
        "purpose": "Crawls for Alexa and Amazon AI product improvement.",
        "respects_robots_txt": "yes",
        "source": "developer.amazon.com/amazonbot",
    },

    # ---------------- Apple ----------------
    {
        "name": "Applebot",
        "operator": "Apple",
        "category": "search_retrieval",
        "purpose": "Standard crawler powering Siri and Spotlight results.",
        "respects_robots_txt": "yes",
        "source": "support.apple.com/en-us/119829",
    },
    {
        "name": "Applebot-Extended",
        "operator": "Apple",
        "category": "opt_out_token",
        "purpose": "Robots.txt-only token opting content out of Apple Intelligence training.",
        "respects_robots_txt": "yes",
        "source": "support.apple.com/en-us/119829",
    },

    # ---------------- Meta ----------------
    {
        "name": "FacebookBot",
        "operator": "Meta",
        "category": "training",
        "purpose": "Crawls public content for Meta's AI products.",
        "respects_robots_txt": "yes",
        "source": "developers.facebook.com/docs/sharing/webmasters/web-crawlers",
    },
    {
        "name": "meta-externalagent",
        "operator": "Meta",
        "category": "training",
        "purpose": "Crawls public content for Meta AI training and indexing.",
        "respects_robots_txt": "yes",
        "source": "developers.facebook.com/docs/sharing/webmasters/web-crawlers",
    },

    # ---------------- ByteDance ----------------
    {
        "name": "Bytespider",
        "operator": "ByteDance",
        "category": "training",
        "purpose": "Crawls for ByteDance/TikTok AI model training.",
        "respects_robots_txt": "unclear",
        "source": "widely reported mixed compliance; treat robots.txt directives as best-effort only",
    },

    # ---------------- Common Crawl ----------------
    {
        "name": "CCBot",
        "operator": "Common Crawl",
        "category": "training",
        "purpose": "Builds the open Common Crawl dataset, used to train many LLMs across multiple labs (not just one company).",
        "respects_robots_txt": "yes",
        "source": "commoncrawl.org/faq",
    },

    # ---------------- Other notable agents ----------------
    {
        "name": "DuckAssistBot",
        "operator": "DuckDuckGo",
        "category": "search_retrieval",
        "purpose": "Powers DuckDuckGo's AI-assisted answer features.",
        "respects_robots_txt": "yes",
        "source": "duckduckgo.com/duckduckgo-help-pages/results/duckassistbot",
    },
    {
        "name": "MistralAI-User",
        "operator": "Mistral AI",
        "category": "on_demand",
        "purpose": "On-demand fetch triggered by a Le Chat user referencing a URL.",
        "respects_robots_txt": "yes",
        "source": "docs.mistral.ai (bots)",
    },
    {
        "name": "cohere-ai",
        "operator": "Cohere",
        "category": "training",
        "purpose": "Crawls for Cohere model training.",
        "respects_robots_txt": "yes",
        "source": "cohere.com robots documentation",
    },
    {
        "name": "Diffbot",
        "operator": "Diffbot",
        "category": "training",
        "purpose": "Structured web-data extraction, used as a data source by several AI products.",
        "respects_robots_txt": "unclear",
        "source": "docs.diffbot.com — compliance varies by product configuration",
    },
]


def get_by_category(category: str) -> list:
    return [b for b in AI_CRAWLERS if b["category"] == category]


def get_by_name(name: str) -> dict:
    for b in AI_CRAWLERS:
        if b["name"].lower() == name.lower():
            return b
    return None
