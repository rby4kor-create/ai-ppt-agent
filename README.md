# Top Gen AI - Weekly GenAI Intelligence Report Generator

Generates a premium, one-topic-per-slide weekly AI intelligence briefing
(`Top Gen AI Advances: CWxx, 2026`) as a PowerPoint deck, from RSS feeds
across trusted AI labs and independent tech press.

## Installation

```bash
pip install -r requirements.txt
```

## Environment

Copy `.env.example` to `.env` and fill in what you have:

```env
OPENROUTER_API_KEY=      # real AI analysis; without it, a deterministic template writer is used
UNSPLASH_ACCESS_KEY=     # optional - live per-category stock photo fallback
PEXELS_API_KEY=          # primary provider for the 200-image visual library (see below)
```

Only `OPENROUTER_API_KEY` is required for good content. The image keys are
optional - generation always works, falling back to bundled local
illustrations if no image key/library is available.

## Run the frontend

```bash
streamlit run ui.py
```

Navigate to **Generate Report** to run the pipeline, or **Visual Library** to
browse/filter the local image library (category, provider, quality score,
search by tag). Select RSS sources, categories/topics, and theme on the
Generate Report page, tick which candidate articles become slides, then
generate. Each ticked topic shows its auto-selected image with two
alternatives (from the local library) - override is optional, auto-select
is the default. The output `.pptx` is written to `output/`.

## Building the 200-image visual library (recommended, one-time setup)

By default, topic slides fall back to a live single-photo Unsplash fetch
or a small set of bundled local illustrations. For premium, varied,
non-repetitive imagery, build the curated local library once:

```bash
python tools/download_images.py
```

This reads `config/visual_taxonomy.json` (15 categories - frontier
models, developer AI, robotics, infrastructure, healthcare, etc.),
searches Pexels (primary) and Unsplash (secondary) for each category's
preferred queries, and downloads ~12-15 high-resolution (2000px+)
landscape images per category into `assets/stock/<category>/`, recording
full provenance (source URL, photographer, license, retrieval date,
quality score) in `assets/manifest/image_manifest.json`.

It's safe to re-run - already-downloaded images (by provider+photo ID)
are skipped, so this only tops each category up toward its target count.
Requires `PEXELS_API_KEY` and/or `UNSPLASH_ACCESS_KEY`; without either,
it prints a setup message and exits cleanly (generation still works from
whatever's already local).

Then validate and inspect it:

```bash
python tools/deduplicate_images.py --apply   # remove near-duplicates (perceptual hash)
python tools/validate_images.py              # QA report -> qa/image_library_report.md
python tools/generate_contact_sheets.py       # visual grid -> assets/previews/*.jpg
```

Once built, normal weekly generation reads the library **locally** -
no network call or API key needed at generation time. Each topic's image
is chosen automatically by `ImageAgent.select_image_for_topic()`
(`agents/image_agent.py`), which ranks the category's candidates by
semantic relevance to the story's title/keywords, composition/aspect-ratio
fit for the slide's layout, editorial quality, and resolution - never a
random pick, and it avoids reusing an image already placed elsewhere in
the same deck when a good alternative exists.

## Generate a report (headless / scripted)

The frontend (`app.py`) calls the same pipeline the Streamlit UI does:
`agents/analysis_agent.py` -> `agents/presentation_builder.py` ->
`agents/powerpoint_agent.py`. See `app.py` for the exact call sequence if
you want to script a run outside Streamlit.

## Design system

All colors, fonts, and spacing constants live in `models/theme.py`
(`Theme` class) and the layout constants at the top of
`agents/powerpoint_agent.py`. Two palettes ship: `"Modern Executive"`
(dark, gold-accent, default) and `"Bosch Corporate"` (light). Switch with
the theme selector in the frontend, or `PowerPointAgent().generate(presentation, theme="...")`.

## Topic/category configuration

RSS sources and their trust tier live in `config.py` (`RSS_FEEDS`,
`SOURCE_TIER`). The image-selection categories live in
`config/visual_taxonomy.json`.
