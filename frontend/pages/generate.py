"""
Generate -- "Create Intelligence Brief". A guided, editorial creation
studio replacing the old dropdown/radio/button stack. Every control
still feeds exactly the same backend calls as before
(collect_candidates / generate_from_selection in app.py) -- only the
presentation changed.

Workflow:
  01 TIMEFRAME       -> start_date / end_date
  02 SOURCES         -> RSS_FEEDS subset
  03 VISUAL DIRECTION -> cosmetic style, best-effort mapped to Theme
  04 PRESENTATION    -> Theme, max topics, toggles
  -- Find Topics --
  05 SELECT TOPICS   -> tick real candidate articles, per category
  -- Generate Executive Brief --
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

from config import RSS_FEEDS, MAX_SELECTED_TOPICS
from models.theme import Theme
from agents.image_agent import ImageAgent, CATEGORY_TO_TAXONOMY
from frontend.activity_log import log_event
from app import collect_candidates, generate_from_selection

FETCH_STAGES = [
    "Fetching RSS articles...",
    "Removing duplicates...",
    "Categorizing articles...",
    "Ready for topic selection",
]
GENERATE_STAGES = [
    "Running AI analysis...",
    "Building presentation...",
    "Generating PowerPoint...",
    "Completed",
]

VISUAL_DIRECTIONS = ["AI curated", "Editorial", "Data-driven", "Executive"]
# Best-effort mapping onto the two real backend palettes -- the UI
# offers four directions per the brief, the backend supports two, so
# each maps onto the closer of the two rather than inventing a third
# palette that wouldn't actually render differently in the deck.
DIRECTION_TO_THEME = {
    "AI curated": "Bosch Corporate",
    "Data-driven": "Bosch Corporate",
    "Editorial": "Modern Executive",
    "Executive": "Modern Executive",
}


def _week_bounds(offset_weeks=0):
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    if offset_weeks == 0:
        return this_monday, today
    return this_monday - timedelta(days=7), this_monday - timedelta(days=1)


def _render_progress(container, stages, completed_stages):
    rows = []
    for i, stage in enumerate(stages, start=1):
        done = stage in completed_stages
        is_last_done = done and stage == completed_stages[-1] if completed_stages else False
        css = "progress-row done" if done else "progress-row"
        mark = "✓" if done else str(i).zfill(2)
        rows.append(
            f'<div class="{css}"><span class="progress-mark">{mark}</span>{stage.rstrip(".")}</div>'
        )
    container.markdown("\n".join(rows), unsafe_allow_html=True)


def _get_image_agent():
    if "image_agent" not in st.session_state:
        st.session_state["image_agent"] = ImageAgent()
    return st.session_state["image_agent"]


def _image_preview_for_article(article, category):
    if CATEGORY_TO_TAXONOMY.get(category) is None:
        return

    agent = _get_image_agent()
    candidates = agent.select_top_candidates(
        category, title=article.title, keywords=getattr(article, "key_technologies", None), n=3,
    )
    if not candidates:
        return

    overrides = st.session_state.setdefault("image_overrides", {})
    options = ["Auto-select (recommended)"] + [
        f"Alternative {i} · {round(c['score'] * 100)}% match" for i, c in enumerate(candidates[1:], start=1)
    ]

    cols = st.columns([1, 3])
    with cols[0]:
        st.image(candidates[0]["path"], width=140, caption=f"Recommended · {round(candidates[0]['score'] * 100)}% match")
    with cols[1]:
        choice = st.radio(
            "Image", options, key=f"imgchoice_{article.link}", horizontal=True, label_visibility="collapsed",
        )
        if choice == options[0]:
            overrides.pop(article.link, None)
        else:
            idx = options.index(choice)
            overrides[article.link] = candidates[idx]["path"]
        if len(candidates) > 1:
            alt_cols = st.columns(len(candidates) - 1)
            for alt_col, cand in zip(alt_cols, candidates[1:]):
                with alt_col:
                    st.image(cand["path"], width=90)


def _reset_candidates():
    for key in ("candidates", "candidate_meta", "selected_links", "image_overrides"):
        st.session_state.pop(key, None)


def _step_header(num, title, desc):
    st.markdown(
        f'<div class="step-num active">{num}</div>' if False else "", unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div style="display:flex;gap:18px;margin-top:26px;">
    <div style="font-family:Manrope,sans-serif;font-weight:800;font-size:13px;color:#E2001A;flex:0 0 28px;padding-top:2px;">{num}</div>
    <div style="flex:1;">
        <div class="step-heading">{title}</div>
        <div class="step-desc">{desc}</div>
    </div>
</div>
""".strip(),
        unsafe_allow_html=True,
    )


def _intake_form():
    st.markdown(
        '<div class="section-head"><div class="section-title">Create Intelligence Brief</div>'
        '<div class="section-note">Guided workflow</div></div>',
        unsafe_allow_html=True,
    )

    _step_header("01", "Timeframe", "Choose the reporting window for this brief.")
    report = st.radio("Timeframe", ["This week", "Last week", "Custom range"], label_visibility="collapsed", horizontal=True)
    if report == "Custom range":
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("Start", date.today() - timedelta(days=7))
        with c2:
            end_date = st.date_input("End", date.today())
    elif report == "Last week":
        start_date, end_date = _week_bounds(offset_weeks=1)
    else:
        start_date, end_date = _week_bounds(offset_weeks=0)

    _step_header("02", "Sources", "Choose which intelligence sources feed this brief.")
    source_names = list(RSS_FEEDS.keys())
    selected_sources = st.multiselect(
        "Sources", source_names, default=source_names[:5], label_visibility="collapsed",
    )

    _step_header("03", "Visual Direction", "Set the visual tone the deck should be built around.")
    visual_direction = st.radio(
        "Visual direction", VISUAL_DIRECTIONS, label_visibility="collapsed", horizontal=True,
    )

    _step_header("04", "Presentation", "Configure the deck itself.")
    p1, p2 = st.columns(2)
    with p1:
        theme_override = st.selectbox(
            "Theme", ["Match visual direction"] + Theme.NAMES,
            help="Bosch Corporate: white/light, red accent. Modern Executive: dark navy, gold accent, full-bleed photography.",
        )
        max_topics = st.slider("Max topic slides", min_value=3, max_value=12, value=MAX_SELECTED_TOPICS)
    with p2:
        generate_images = st.toggle("Generate Images", True)
        executive_summary = st.toggle("Executive Summary", True)
        references = st.toggle("References", True)

    theme = DIRECTION_TO_THEME[visual_direction] if theme_override == "Match visual direction" else theme_override

    return {
        "start_date": datetime.combine(start_date, datetime.min.time()),
        "end_date": datetime.combine(end_date, datetime.max.time().replace(microsecond=0)),
        "sources": selected_sources or source_names,
        "theme": theme,
        "generate_images": generate_images,
        "show_executive_summary": executive_summary,
        "show_references": references,
        "max_topics": max_topics,
    }


def render():
    config = _intake_form()

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    fetch_clicked = st.button("Find Topics", use_container_width=True)

    if fetch_clicked:
        _reset_candidates()
        log_event("topics_fetch_started", {"sources": len(config["sources"])})
        status_box = st.empty()
        progress_box = st.empty()
        completed = []
        _render_progress(progress_box, FETCH_STAGES, completed)

        def on_fetch_progress(stage, pct):
            if stage not in completed:
                completed.append(stage)
            _render_progress(progress_box, FETCH_STAGES, completed)
            status_box.info(stage)

        try:
            data = collect_candidates(
                start_date=config["start_date"],
                end_date=config["end_date"],
                sources=config["sources"],
                candidate_pool_size=40,
                progress_callback=on_fetch_progress,
            )
            st.session_state["candidates"] = data["articles"]
            st.session_state["candidate_meta"] = {
                "collected": data["collected"],
                "after_dedup": data["after_dedup"],
                "skipped_collection": data["skipped_collection"],
            }
            top_links = {a.link for a in data["articles"][: config["max_topics"]]}
            st.session_state["selected_links"] = top_links
            status_box.success(f"Found {len(data['articles'])} candidate article(s). Review and select below.")
            log_event("topics_fetch_completed", {"found": len(data["articles"])})
        except Exception as e:
            status_box.error(f"Topic fetch failed: {e}")
            st.exception(e)
            log_event("topics_fetch_failed", {"error": str(e)[:200]})

    candidates = st.session_state.get("candidates")

    if not candidates:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-eyebrow">Ready When You Are</div>'
            '<div class="empty-title">Click Find Topics to pull this week&rsquo;s candidate articles</div>'
            '<div class="empty-sub">Nothing is auto-picked without your review -- '
            'you choose exactly which stories become slides.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    meta = st.session_state.get("candidate_meta", {})
    st.markdown(
        f'<div class="section-note" style="margin-top:24px;">'
        f'{meta.get("collected", len(candidates))} collected &rarr; '
        f'{meta.get("after_dedup", len(candidates))} after de-dup &rarr; '
        f'{len(candidates)} candidates shown, ranked by relevance.</div>',
        unsafe_allow_html=True,
    )

    selected_links = st.session_state.setdefault("selected_links", set())

    _step_header("05", "Select Topics", "Tick which stories become their own slide.")

    by_category = defaultdict(list)
    for article in candidates:
        by_category[article.category or "Uncategorized"].append(article)

    for category, articles in sorted(by_category.items(), key=lambda kv: -len(kv[1])):
        with st.expander(f"{category}  ·  {len(articles)} article(s)", expanded=True):
            for article in articles:
                checked = article.link in selected_links
                new_val = st.checkbox(
                    f"**{article.title}**  \n*{article.source} — {article.published:%d %b}*",
                    value=checked,
                    key=f"topic_{article.link}",
                )
                if new_val and not checked:
                    selected_links.add(article.link)
                    log_event("topic_selected", {"title": article.title[:80]})
                elif not new_val and checked:
                    selected_links.discard(article.link)
                    log_event("topic_deselected", {"title": article.title[:80]})
                elif new_val:
                    selected_links.add(article.link)
                else:
                    selected_links.discard(article.link)

                if new_val:
                    _image_preview_for_article(article, category)

    st.session_state["selected_links"] = selected_links
    n_selected = len(selected_links)
    st.markdown(
        f'<div style="font-weight:700;margin-top:8px;">{n_selected} topic(s) selected'
        f'{" — each becomes its own slide." if n_selected else ""}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    generate_clicked = st.button(
        "Generate Intelligence Brief", use_container_width=True, type="primary", disabled=n_selected == 0,
    )

    if generate_clicked:
        selected_articles = [a for a in candidates if a.link in selected_links]
        log_event("generation_started", {"topics": len(selected_articles), "theme": config["theme"]})

        status_box = st.empty()
        progress_box = st.empty()
        completed = []
        _render_progress(progress_box, GENERATE_STAGES, completed)

        def on_gen_progress(stage, pct):
            if stage not in completed:
                completed.append(stage)
            _render_progress(progress_box, GENERATE_STAGES, completed)
            status_box.info(stage)

        try:
            overrides = {
                link: path for link, path in st.session_state.get("image_overrides", {}).items()
                if link in selected_links
            }
            stats = generate_from_selection(
                selected_articles,
                theme=config["theme"],
                max_topics=config["max_topics"],
                progress_callback=on_gen_progress,
                image_overrides=overrides,
            )
            stats["sources"] = config["sources"]
            st.session_state["last_run"] = stats

            history = st.session_state.setdefault("report_history", [])
            history.insert(0, {**stats, "generated_at": datetime.now(), "theme": config["theme"]})

            status_box.success("PowerPoint generated successfully.")
            log_event("generation_completed", {"slides": stats["slides"], "analyzed": stats["analyzed"]})

            llm_count = stats["diagnostics"]["llm"]
            template_count = stats["diagnostics"]["template_fallback"]
            if llm_count == 0 and template_count > 0:
                st.error(
                    f"All {template_count} article(s) were written by the template fallback, not the "
                    "LLM — content will repeat across slides. Check OPENROUTER_API_KEY in your .env file."
                )
            elif template_count > 0:
                st.warning(
                    f"{template_count} of {template_count + llm_count} article(s) used the template "
                    "fallback (the LLM call failed for those specific articles)."
                )

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Selected", stats["selected"])
            m2.metric("Analyzed", stats["analyzed"])
            m3.metric("Images", stats["images_resolved"])
            m4.metric("Slides", stats["slides"])

            ppt_path = stats["pptx_path"]
            if Path(ppt_path).exists():
                with open(ppt_path, "rb") as file:
                    downloaded = st.download_button(
                        "Download PowerPoint",
                        data=file,
                        file_name="Weekly_GenAI_Report.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True,
                    )
                if downloaded:
                    log_event("report_downloaded", {"slides": stats["slides"]})
            else:
                st.error("PowerPoint file was not found after generation.")

        except Exception as e:
            status_box.error(f"Generation failed: {e}")
            st.exception(e)
            log_event("generation_failed", {"error": str(e)[:200]})
