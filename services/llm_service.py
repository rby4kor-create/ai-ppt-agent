import json
import os
import time

from config import OPENROUTER_MODEL, TEMPERATURE, MAX_TOKENS, MAX_RETRIES, RETRY_DELAY
from utils.logger import get_logger
from models.executive_analysis import ExecutiveAnalysis

logger = get_logger(__name__)


class LLMService:
    """
    Handles all communication with the LLM (via OpenRouter's OpenAI-
    compatible API). Returns ExecutiveAnalysis objects so callers never
    deal with raw JSON.
    """

    def __init__(self):
        # Imported lazily so the whole pipeline doesn't hard-fail at
        # import time in environments where the `openai` package isn't
        # installed and USE_LLM=False (offline/template-only mode).
        from openai import OpenAI

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model = OPENROUTER_MODEL

    def generate_analysis(self, article, article_text):
        """
        Sends the article to the LLM and returns an ExecutiveAnalysis
        object. Raises on failure (retries are handled in call_llm) -
        callers are expected to catch and fall back to the template
        agent, never to silently drop the article.
        """
        prompt = self.build_prompt(article, article_text)
        response = self.call_llm(prompt)
        content = response.choices[0].message.content
        return self.parse_response(content, article)

    def call_llm(self, prompt):
        """Calls the LLM with automatic retry support."""

        last_exception = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Calling LLM (attempt {attempt}/{MAX_RETRIES})")

                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a Principal AI Strategy Consultant who prepares "
                                "executive intelligence reports for enterprise leadership. "
                                "You analyze ONLY the supplied article. You do not invent "
                                "facts or make unsupported claims, and you never use generic "
                                "filler phrasing - every sentence must be specific to this "
                                "article. You return valid JSON only, with no markdown "
                                "make sure each slide contains each topic.no continuation of that topic"
                                "fences and no commentary outside the JSON object."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                )

                logger.info("LLM response received successfully.")
                return response

            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)

        logger.error("All retry attempts failed.")
        raise last_exception

    def build_prompt(self, article, article_text):

        content_block = article_text.strip() if article_text else (
            "(No article body/description was available beyond the title - "
            "analyze conservatively and avoid inventing specifics you cannot "
            "support from the title and category alone.)"
        )

        return f"""You are an Enterprise AI Strategy Consultant.

Analyze ONLY the following AI news item for enterprise leadership. Do not
invent facts. Do not make unsupported claims. Do not use generic phrases
like "reflects a broader trend" or "worth monitoring" - extract what is
actually specific about THIS article.

ARTICLE
Title: {article.title}
Source: {article.source}
Category: {article.category}
Published: {article.published.strftime("%d %B %Y") if article.published else "unknown"}

CONTENT
{content_block}

Return ONLY valid JSON matching exactly this shape (no markdown, no extra
keys, no commentary):

{{
  "executive_summary": "",
  "business_impact": "",
  "technical_analysis": "",
  "enterprise_recommendation": "",
  "future_outlook": "",
  "strategic_importance": "",
  "innovation_score": 0,
  "enterprise_readiness": 0,
  "confidence_score": 0.0,
  "risk_level": "Low|Medium|High",
  "implementation_effort": "Low|Medium|High",
  "key_takeaways": [],
  "key_technologies": [],
  "keywords": [],
  "industry_impact": [],
  "opportunities": [],
  "risks": []
}}

Rules:
- executive_summary, business_impact, technical_analysis: max 35 words each, presentation-ready, specific to this article.
- enterprise_recommendation, strategic_importance: max 30 words each, a concrete recommendation/observation, not a platitude.
- innovation_score and enterprise_readiness: integers 0-10, justified by evidence in the article.
- confidence_score: 0.0-1.0, your confidence in this analysis given how much real content was available.
- key_technologies, keywords: max 5 items each.
- key_takeaways, industry_impact, opportunities, risks: max 3 items each, short phrases.
"""

    def parse_response(self, response, article):
        """Converts the model's JSON response into an ExecutiveAnalysis."""

        def shorten(text, max_words=35):
            if not text:
                return ""
            words = str(text).split()
            if len(words) <= max_words:
                return str(text)
            return " ".join(words[:max_words]) + "..."

        def as_list(value, max_items=5):
            if not value:
                return []
            if isinstance(value, str):
                value = [value]
            return [str(v) for v in list(value)[:max_items]]

        def as_number(value, default=0.0):
            try:
                return float(str(value).replace("/10", "").strip())
            except (TypeError, ValueError):
                return default

        cleaned = response.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response: {response[:500]}")
            raise

        return ExecutiveAnalysis(
            title=article.title,
            category=article.category,
            source=article.source,
            article_url=article.link,
            published=article.published,
            executive_summary=shorten(data.get("executive_summary", ""), 35),
            business_impact=shorten(data.get("business_impact", ""), 30),
            technical_analysis=shorten(data.get("technical_analysis", ""), 35),
            enterprise_recommendation=shorten(data.get("enterprise_recommendation", ""), 30),
            future_outlook=shorten(data.get("future_outlook", ""), 30),
            strategic_importance=shorten(data.get("strategic_importance", ""), 30),
            innovation_score=as_number(data.get("innovation_score", 5)),
            enterprise_readiness=as_number(data.get("enterprise_readiness", 5)),
            confidence_score=as_number(data.get("confidence_score", 0.7)),
            risk_level=data.get("risk_level", "Medium"),
            implementation_effort=data.get("implementation_effort", "Medium"),
            key_takeaways=as_list(data.get("key_takeaways", []), 3),
            key_technologies=as_list(data.get("key_technologies", []), 5),
            keywords=as_list(data.get("keywords", []), 5),
            industry_impact=as_list(data.get("industry_impact", []), 3),
            opportunities=as_list(data.get("opportunities", []), 3),
            risks=as_list(data.get("risks", []), 3),
            generated_by="llm",
        )
