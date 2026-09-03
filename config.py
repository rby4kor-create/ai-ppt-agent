# config.py

from dotenv import load_dotenv

# Loads OPENROUTER_API_KEY (and anything else) from a .env file in the
# project root into os.environ. Without this call, a .env file is
# silently ignored - os.getenv("OPENROUTER_API_KEY") in
# services/llm_service.py and agents/analysis_agent.py would read as
# None even with a correctly filled-in .env, and every article would
# silently fall back to TemplateAnalysisAgent with no error at all.
load_dotenv()

RSS_FEEDS = {
    # --- Tier 1: primary/official sources (labs, research orgs, cloud vendors) ---
    "OpenAI": "https://openai.com/news/rss.xml",
    "Anthropic": "https://www.anthropic.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/discover/blog/rss.xml",
    "Microsoft AI": "https://blogs.microsoft.com/ai/feed/",
    "NVIDIA": "https://blogs.nvidia.com/feed/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "AWS Machine Learning": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "Azure": "https://azure.microsoft.com/en-us/blog/feed/",
    "Google Cloud": "https://cloud.google.com/blog/products/ai-machine-learning/rss/",
    "Meta AI": "https://ai.meta.com/blog/rss/",
    # --- Tier 2: independent/press blogs, used to broaden weekly coverage
    # ("many blogs") beyond just the labs' own announcements, and to
    # surface stories a single vendor blog wouldn't cover. ---
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica AI": "https://arstechnica.com/ai/feed/",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "IEEE Spectrum AI": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
    "MIT Technology Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
}

# Source credibility tier, used for the "trusted source" policy: Tier 1
# (official/primary) is preferred when a story exists in multiple feeds;
# Tier 2 (independent press) broadens coverage and is grouped separately
# wherever sources are listed/reported on.
SOURCE_TIER = {
    "OpenAI": 1, "Anthropic": 1, "Google DeepMind": 1, "Microsoft AI": 1,
    "NVIDIA": 1, "Hugging Face": 1, "AWS Machine Learning": 1, "Azure": 1,
    "Google Cloud": 1, "Meta AI": 1,
    "TechCrunch AI": 2, "VentureBeat AI": 2, "The Verge AI": 2,
    "Ars Technica AI": 2, "Wired AI": 2, "IEEE Spectrum AI": 2,
    "MIT Technology Review AI": 2,
}

# ---------------------------------------------------------------------------
# Article selection
# ---------------------------------------------------------------------------

# Target number of topic slides. If fewer valid articles survive the
# pipeline, the deck simply has fewer topic slides - we never fabricate
# articles to hit this number (see TopicSelectionAgent / run_pipeline).
MAX_SELECTED_TOPICS = 8

# Minimum number of topics a category needs (among selected topics) to get
# its own section divider slide. Categories below this threshold are still
# included as topic slides, just without a divider.
MIN_TOPICS_FOR_SECTION_DIVIDER = 2

# ---------------------------------------------------------------------------
# LLM (OpenRouter) settings
# ---------------------------------------------------------------------------

# Master switch. When False (or when OPENROUTER_API_KEY is unset), the
# pipeline uses the deterministic TemplateAnalysisAgent fallback instead of
# calling an LLM - this keeps the pipeline runnable offline / without a key,
# while still producing a full, schema-consistent ExecutiveAnalysis per
# article. See agents/analysis_agent.py.
USE_LLM = True

OPENROUTER_MODEL = "openai/gpt-4o-mini"
TEMPERATURE = 0.4
MAX_TOKENS = 900
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

OUTPUT_DIR = "output"
OUTPUT_FILENAME = "Weekly_GenAI_Report.pptx"
