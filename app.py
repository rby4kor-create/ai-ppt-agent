"""
Pipeline entry point. Exposes run_pipeline(), which the Streamlit
frontend (frontend/home.py) imports and calls - previously this file
was a bare top-level script with no callable function, so the frontend
import (`from app import run_pipeline`) failed immediately.

Also implements the diagnostic logging the brief requires: exact counts
at every pipeline stage, and a per-article reason for anything dropped,
so "only 2 articles in the deck" is always traceable to a specific
stage instead of requiring re-investigation each time.
"""
from datetime import datetime, timedelta

from config import RSS_FEEDS, MAX_SELECTED_TOPICS, OUTPUT_DIR
from utils.logger import get_logger

from agents.search_agent import SearchAgent
from agents.ranking_agent import RankingAgent
from agents.duplicate_agent import DuplicateAgent
from agents.categorization_agent import CategorizationAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.topic_selection_agent import TopicSelectionAgent
from agents.analysis_agent import AnalysisAgent
from agents.executive_summary_agent import ExecutiveSummaryAgent
from agents.presentation_builder import PresentationBuilder
from agents.powerpoint_agent import PowerPointAgent

logger = get_logger(__name__)


def _default_week_range():
    """Most recently completed Mon-Sun week."""
    today = datetime.now()
    last_monday = today - timedelta(days=today.weekday() + 7)
    start = datetime(last_monday.year, last_monday.month, last_monday.day)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def collect_candidates(
    start_date=None,
    end_date=None,
    sources=None,
    candidate_pool_size=40,
    progress_callback=None,
):
    """
    Steps 1-4 only: fetch -> rank -> dedupe -> categorize. Returns the
    full categorized candidate pool (capped at `candidate_pool_size`,
    highest-scored first) instead of running topic selection/analysis/
    render, so the frontend can show the user every real candidate
    article - grouped by category, with its real title and source - and
    let them tick which ones become slides, rather than the deck always
    being auto-picked with no visibility into what was left out.

    Returns a dict: {"articles": [...], "collected", "after_dedup",
    "skipped_collection", "sources"}.
    """

    def report(stage, pct):
        logger.info(f"[{pct:>3}%] {stage}")
        if progress_callback:
            progress_callback(stage, pct)

    if start_date is None or end_date is None:
        start_date, end_date = _default_week_range()

    feeds = RSS_FEEDS
    if sources:
        feeds = {k: v for k, v in RSS_FEEDS.items() if k in sources}
        if not feeds:
            logger.warning("Requested sources matched nothing in RSS_FEEDS; using all sources.")
            feeds = RSS_FEEDS

    logger.info("=" * 70)
    logger.info("COLLECTING CANDIDATE ARTICLES")
    logger.info("=" * 70)
    logger.info(f"Date range : {start_date:%d-%b-%Y} - {end_date:%d-%b-%Y}")
    logger.info(f"Sources    : {', '.join(feeds.keys())}")

    report("Fetching RSS articles...", 15)
    search = SearchAgent()
    result = search.fetch_articles(start_date, end_date, max_articles_per_source=20, feeds=feeds)

    collected = len(result.articles)
    logger.info(f"Collected (post date-filter): {collected}")
    for source, count in result.statistics.items():
        logger.info(f"  {source:<28} {count} articles")

    if collected == 0:
        logger.warning(
            "Zero articles survived collection for this date range/source set. "
            "Check the date range against when these feeds actually publish, "
            "and check RSS_FEEDS URLs are still valid."
        )

    ranking = RankingAgent()
    ranked_articles = ranking.rank_articles(result.articles)

    report("Removing duplicates...", 45)
    duplicate_agent = DuplicateAgent()
    unique_articles = duplicate_agent.remove_duplicates(ranked_articles)
    logger.info(f"After duplicate removal: {len(unique_articles)} (removed {collected - len(unique_articles)})")

    report("Categorizing articles...", 75)
    categorizer = CategorizationAgent()
    categorized_articles = categorizer.categorize(unique_articles)
    categorized_articles = sorted(categorized_articles, key=lambda a: a.score, reverse=True)
    logger.info(f"After categorization: {len(categorized_articles)}")

    report("Ready for topic selection", 100)

    return {
        "articles": categorized_articles[:candidate_pool_size],
        "collected": collected,
        "after_dedup": len(unique_articles),
        "sources": list(feeds.keys()),
        "skipped_collection": result.skipped,
    }


def generate_from_selection(
    selected_articles,
    theme=None,
    max_topics=None,
    progress_callback=None,
    image_overrides=None,
):
    """
    Steps 5-8 only: takes articles the user has already picked (e.g. via
    the frontend's topic-selection checklist) and turns them straight
    into a rendered .pptx - no further automatic re-selection. Still
    caps at `max_topics` (via TopicSelectionAgent's per-source cap) if
    the user ticked more than that, so a manual selection can't produce
    an unbounded deck.

    `image_overrides`, if given, is {article.link: local_image_path} -
    populated by the frontend's Story -> Recommended/Alternative visual
    preview (frontend/home.py `_image_preview_for_article`) when someone
    picks an alternative instead of the auto-selected image. Topics not
    present in the dict keep the normal automatic selection.
    """

    def report(stage, pct):
        logger.info(f"[{pct:>3}%] {stage}")
        if progress_callback:
            progress_callback(stage, pct)

    max_topics = max_topics or MAX_SELECTED_TOPICS

    if max_topics and len(selected_articles) > max_topics:
        knowledge_agent = KnowledgeAgent()
        repository = knowledge_agent.build_repository(selected_articles)
        selector = TopicSelectionAgent()
        selected_articles = selector.select_topics(repository, max_topics=max_topics)

    logger.info(f"Generating from {len(selected_articles)} user-selected article(s), theme={theme!r}")

    report("Running AI analysis...", 25)
    analysis_agent = AnalysisAgent()
    analyses, diagnostics = analysis_agent.analyze(selected_articles)

    logger.info(
        f"Successfully analyzed: {len(analyses)} "
        f"(LLM: {diagnostics['llm']}, template fallback: {diagnostics['template_fallback']})"
    )
    if diagnostics["llm"] == 0 and diagnostics["template_fallback"] > 0:
        logger.warning(
            "!" * 70 + "\n"
            f"ALL {diagnostics['template_fallback']} article(s) used the template "
            "fallback - the LLM was not used for a single one. The deck will read "
            "as repetitive because it's drawing from a small fixed phrase pool.\n"
            "See the LLM warning earlier in this log for why, and fix "
            "OPENROUTER_API_KEY before regenerating.\n" + "!" * 70
        )
    if diagnostics["skipped"]:
        logger.info(f"Dropped during analysis: {len(diagnostics['skipped'])}")
        for s in diagnostics["skipped"]:
            logger.info(f"  - [{s['source']}] '{s['title'][:60]}' -> {s['reason']}")

    report("Building presentation...", 60)
    summary_agent = ExecutiveSummaryAgent()
    executive_summary = summary_agent.generate_summary(analyses)

    builder = PresentationBuilder()
    presentation = builder.build(analyses, executive_summary, image_overrides=image_overrides)

    report("Generating PowerPoint...", 85)
    powerpoint = PowerPointAgent()
    ppt_path = powerpoint.generate(presentation, theme=theme)

    report("Completed", 100)

    logger.info("=" * 70)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Selected             : {len(selected_articles)}")
    logger.info(f"Successfully analyzed: {len(analyses)}")
    logger.info(f"Final topic slides   : {len(presentation.slides)}")
    logger.info(f"Output               : {ppt_path}")
    logger.info("=" * 70)

    images_resolved = sum(1 for s in presentation.slides if s.image_path)
    avg_innovation = (
        sum(a.innovation_score for a in analyses) / len(analyses) if analyses else 0.0
    )
    readiness_pct = (
        sum(float(a.enterprise_readiness) for a in analyses) / len(analyses) * 10
        if analyses else 0.0
    )

    return {
        "pptx_path": ppt_path,
        "selected": len(selected_articles),
        "analyzed": len(analyses),
        "images_resolved": images_resolved,
        "slides": len(presentation.slides) + 6,  # + non-topic slides (cover, overview, signals, takeaways, references, ~1 divider)
        "avg_innovation": avg_innovation,
        "readiness_pct": readiness_pct,
        "diagnostics": diagnostics,
    }


def run_pipeline(
    start_date=None,
    end_date=None,
    sources=None,
    max_topics=None,
    theme=None,
    progress_callback=None,
):
    """
    Fully automatic collection -> analysis -> presentation pipeline
    (collect_candidates + TopicSelectionAgent's automatic pick +
    generate_from_selection combined), for callers that don't need the
    interactive topic-selection step - e.g. `python app.py`, or a
    scheduled/headless weekly run.
    """
    max_topics = max_topics or MAX_SELECTED_TOPICS

    collected_data = collect_candidates(
        start_date=start_date, end_date=end_date, sources=sources,
        candidate_pool_size=200, progress_callback=progress_callback,
    )

    knowledge_agent = KnowledgeAgent()
    repository = knowledge_agent.build_repository(collected_data["articles"])
    selector = TopicSelectionAgent()
    selected_articles = selector.select_topics(repository, max_topics=max_topics)

    if len(selected_articles) < max_topics:
        logger.warning(
            f"Only {len(selected_articles)} article(s) available - fewer than the "
            f"target of {max_topics}. The deck will contain {len(selected_articles)} "
            f"topic slides. This is NOT padded with fake articles; if you expect "
            f"more, widen the date range or check RSS_FEEDS."
        )

    result = generate_from_selection(
        selected_articles, theme=theme, max_topics=max_topics,
        progress_callback=progress_callback,
    )
    result.update({
        "sources": collected_data["sources"],
        "collected": collected_data["collected"],
        "after_dedup": collected_data["after_dedup"],
        "skipped_collection": collected_data["skipped_collection"],
    })
    return result


if __name__ == "__main__":
    stats = run_pipeline()
    print(f"\nGenerated: {stats['pptx_path']}")
    print(f"Selected {stats['selected']}, analyzed {stats['analyzed']}, slides {stats['slides']}")
