"""
BOSCH AI INTELLIGENCE WORKSPACE -- design system.

Replaces the old "Aurora Editorial" violet/coral gradient system
(frontend/styles.py) entirely. This is the single source of truth for
every color, font, spacing, radius and shadow value used anywhere in
the app -- nothing below should be hardcoded again in a page file.

Direction: editorial + enterprise + intelligence. Warm ivory paper,
graphite and charcoal ink, Bosch red as a controlled accent (never a
wash), one grotesk type family driving the whole hierarchy, square-ish
architectural corners instead of universal rounding, and motion that's
felt rather than seen.
"""
import streamlit as st

# ---------------------------------------------------------------------------
# TOKENS
# ---------------------------------------------------------------------------

# -- Neutrals -----------------------------------------------------------
IVORY = "#F7F5F1"          # app background -- warm off-white, not gray
PAPER = "#FBFAF8"          # raised surface on top of IVORY
CARD = "#FFFFFF"           # cards / panels
GRAPHITE = "#1C1C1E"       # primary ink
GRAPHITE_SOFT = "#4A4A4D"  # secondary text
SLATE = "#63636A"          # tertiary / metadata / captions -- deepened from
                            # #8A8A8E so it clears ~4.6:1 contrast on IVORY/
                            # CARD (was ~3.2:1, borderline-to-failing for
                            # small text) and reads as ink rather than a
                            # near-invisible wash
HAIRLINE = "rgba(28,28,30,0.10)"
HAIRLINE_STRONG = "rgba(28,28,30,0.18)"
CHARCOAL = "#141416"       # deep panel background (hero / footer zones)
CHARCOAL_RAISED = "#1F2023"

# -- Brand ----------------------------------------------------------------
BOSCH_RED = "#E2001A"
BOSCH_RED_DARK = "#B50014"
BOSCH_RED_TINT = "rgba(226,0,26,0.08)"

# -- AI accent (restrained, used sparingly for "signal" states) -----------
SIGNAL = "#3A6B5C"          # deep muted teal-green -- "momentum/positive"
SIGNAL_AMBER = "#B8863A"    # "stable / watch"
SIGNAL_MUTED = "#8A8A8E"    # "flat"

# -- Semantic ---------------------------------------------------------------
SUCCESS = "#3A6B5C"
WARNING = "#B8863A"
DANGER = "#B50014"

FONT_STACK = "'Manrope', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
FONT_DISPLAY = "'Manrope', 'Inter', sans-serif"


def inject_global_css():
    css = f"""
<style>
/* Self-hosted -- NOT pulled from fonts.googleapis.com. That CDN call is
   the actual reason type was failing to load / looked unstyled: many
   corporate and EU networks (Bosch's included) block direct requests to
   Google's font servers, and even when unblocked it's a render-blocking
   best-effort fetch that can lose the race and paint before it lands. The
   files below ship inside the app itself via app/static/fonts (see
   .streamlit/config.toml: enableStaticServing = true), so there is no
   external call to fail. */
@font-face {{
    font-family: 'Manrope';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('app/static/fonts/manrope/manrope-latin-400-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Manrope';
    font-style: normal;
    font-weight: 500;
    font-display: swap;
    src: url('app/static/fonts/manrope/manrope-latin-500-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Manrope';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('app/static/fonts/manrope/manrope-latin-600-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Manrope';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('app/static/fonts/manrope/manrope-latin-700-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Manrope';
    font-style: normal;
    font-weight: 800;
    font-display: swap;
    src: url('app/static/fonts/manrope/manrope-latin-800-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('app/static/fonts/inter/inter-latin-400-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Inter';
    font-style: normal;
    font-weight: 500;
    font-display: swap;
    src: url('app/static/fonts/inter/inter-latin-500-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Inter';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('app/static/fonts/inter/inter-latin-600-normal.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Inter';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('app/static/fonts/inter/inter-latin-700-normal.woff2') format('woff2');
}}

html, body, [class*="css"] {{
    font-family: {FONT_STACK};
}}

/* ---------------- Legibility hard-floor ----------------
   Defensive, high-specificity rules for every native Streamlit control
   (radio, toggle, checkbox, select, multiselect, tabs, captions). These
   never rely on font-load timing or Streamlit's own default text color --
   they set an explicit, always-dark, always-full-opacity value so a
   widget option can never render as pale/invisible text again, whether
   the option is selected or not. */
.stRadio label, .stRadio [data-testid="stMarkdownContainer"] p,
.stCheckbox label, .stCheckbox [data-testid="stMarkdownContainer"] p,
.stToggle label, .stToggle [data-testid="stMarkdownContainer"] p,
.stSelectbox label, .stMultiSelect label,
div[data-baseweb="select"] *, div[data-baseweb="tag"] span,
.stTabs [data-baseweb="tab"] p {{
    color: {GRAPHITE} !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}}

.stRadio [role="radiogroup"] label {{
    padding: 6px 4px;
    transition: opacity .12s ease;
}}
.stRadio [role="radiogroup"] label:hover {{
    opacity: 0.72 !important;
}}

.stCaption, [data-testid="stCaptionContainer"] p {{
    color: {SLATE} !important;
    opacity: 1 !important;
}}

.stToggle [data-testid="stWidgetLabel"] p {{
    font-weight: 600 !important;
}}
/* Toggle track/thumb reactivity -- visible hover + focus affordance,
   not just a flat flip on click */
.stToggle label div[data-baseweb="checkbox"] div {{
    transition: background-color .15s ease, box-shadow .15s ease;
}}
.stToggle label:hover div[data-baseweb="checkbox"] div {{
    box-shadow: 0 0 0 4px {BOSCH_RED_TINT};
}}

/* ---------------- App shell ---------------- */
.stApp {{
    background: {IVORY};
    color: {GRAPHITE};
}}

header[data-testid="stHeader"] {{ display: none; }}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

section[data-testid="stSidebar"] {{
    background: {CHARCOAL};
    border-right: none;
    width: 272px !important;
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 0;
}}

.block-container {{
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}}

h1, h2, h3, h4 {{
    font-family: {FONT_DISPLAY};
    color: {GRAPHITE};
    letter-spacing: -0.01em;
}}

hr {{ border-color: {HAIRLINE} !important; }}

/* ---------------- Kicker / eyebrow labels ---------------- */
.kicker {{
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    color: {SLATE};
    margin-bottom: 6px;
}}

.kicker.on-dark {{ color: rgba(255,255,255,0.55); }}
.kicker.accent {{ color: {BOSCH_RED}; }}

/* ---------------- Top header bar ---------------- */
.workspace-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 18px;
    margin-bottom: 26px;
    border-bottom: 1px solid {HAIRLINE_STRONG};
}}

.workspace-title {{
    font-family: {FONT_DISPLAY};
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.4px;
    color: {GRAPHITE};
}}

.workspace-subtitle {{
    font-size: 12.5px;
    color: {SLATE};
    margin-top: 2px;
}}

.workspace-meta {{
    display: flex;
    gap: 26px;
    text-align: right;
}}

.workspace-meta-item .meta-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {SLATE};
}}

.workspace-meta-item .meta-value {{
    font-size: 13px;
    font-weight: 600;
    color: {GRAPHITE};
    margin-top: 2px;
}}

.status-dot {{
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: {SIGNAL};
    margin-right: 6px;
    box-shadow: 0 0 0 3px rgba(58,107,92,0.15);
}}

/* ---------------- Hero (editorial, dark zone) ---------------- */
.hero-zone {{
    background: {CHARCOAL};
    padding: 56px 48px;
    margin: -1px -1px 32px -1px;
    position: relative;
    overflow: hidden;
}}

.hero-zone::before {{
    content: "";
    position: absolute;
    top: 0; right: 0;
    width: 3px; height: 100%;
    background: {BOSCH_RED};
}}

.hero-eyebrow {{
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 2.4px;
    text-transform: uppercase;
    color: {BOSCH_RED};
    margin-bottom: 18px;
}}

.hero-display {{
    font-family: {FONT_DISPLAY};
    font-size: 46px;
    line-height: 1.05;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
    max-width: 720px;
}}

.hero-narrative {{
    font-size: 16px;
    line-height: 1.6;
    color: rgba(255,255,255,0.72);
    max-width: 560px;
    margin-top: 18px;
}}

.hero-stat-row {{
    display: flex;
    gap: 40px;
    margin-top: 34px;
    padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.12);
}}

.hero-stat .stat-value {{
    font-family: {FONT_DISPLAY};
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
}}

.hero-stat .stat-label {{
    font-size: 10.5px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-top: 2px;
}}

/* ---------------- Section headers ---------------- */
.section-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin: 40px 0 18px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid {HAIRLINE_STRONG};
}}

.section-head .section-title {{
    font-family: {FONT_DISPLAY};
    font-size: 20px;
    font-weight: 800;
    color: {GRAPHITE};
    letter-spacing: -0.01em;
}}

.section-head .section-note {{
    font-size: 12px;
    color: {SLATE};
}}

/* ---------------- Featured brief / report showcase ---------------- */
.brief-shell {{
    display: flex;
    gap: 36px;
    background: {CARD};
    border: 1px solid {HAIRLINE};
    padding: 0;
    margin-bottom: 8px;
}}

.brief-cover-wrap {{
    flex: 0 0 340px;
    position: relative;
    overflow: hidden;
    background: {CHARCOAL};
}}

.brief-cover-wrap img {{
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
    transition: transform .5s cubic-bezier(.2,.8,.2,1);
}}

.brief-body {{
    flex: 1;
    padding: 34px 36px 30px 0;
}}

.brief-eyebrow {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: {BOSCH_RED};
    margin-bottom: 10px;
}}

.brief-title {{
    font-family: {FONT_DISPLAY};
    font-size: 27px;
    font-weight: 800;
    color: {GRAPHITE};
    letter-spacing: -0.01em;
    line-height: 1.15;
}}

.brief-meta {{
    font-size: 13px;
    color: {SLATE};
    margin-top: 10px;
}}

.brief-stats {{
    display: flex;
    gap: 28px;
    margin-top: 22px;
    padding-top: 18px;
    border-top: 1px solid {HAIRLINE};
}}

.brief-stats .b-stat .v {{
    font-family: {FONT_DISPLAY};
    font-size: 19px;
    font-weight: 800;
    color: {GRAPHITE};
}}

.brief-stats .b-stat .l {{
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {SLATE};
}}

/* ---------------- Intelligence signal rows ---------------- */
.signal-row {{
    display: flex;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid {HAIRLINE};
    gap: 20px;
}}

.signal-index {{
    font-family: {FONT_DISPLAY};
    font-size: 13px;
    font-weight: 800;
    color: {SLATE};
    width: 28px;
    flex-shrink: 0;
}}

.signal-name {{
    font-family: {FONT_DISPLAY};
    font-size: 15.5px;
    font-weight: 700;
    color: {GRAPHITE};
    flex: 1;
}}

.signal-meta {{
    font-size: 12px;
    color: {SLATE};
    flex: 0 0 140px;
    text-align: right;
}}

.trend-pill {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .3px;
    padding: 3px 10px;
    border-radius: 3px;
    flex-shrink: 0;
    white-space: nowrap;
}}

.trend-up {{ background: rgba(58,107,92,0.12); color: {SIGNAL}; }}
.trend-flat {{ background: rgba(138,138,142,0.14); color: {SLATE}; }}
.trend-watch {{ background: rgba(184,134,58,0.14); color: {SIGNAL_AMBER}; }}

/* ---------------- Source intelligence ---------------- */
.source-row {{
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid {HAIRLINE};
    font-size: 13.5px;
    gap: 16px;
}}

.source-name {{
    font-weight: 700;
    color: {GRAPHITE};
    flex: 1;
}}

.source-tier {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .8px;
    text-transform: uppercase;
    color: {SLATE};
    flex: 0 0 90px;
}}

.source-count {{
    font-family: {FONT_DISPLAY};
    font-weight: 800;
    color: {GRAPHITE};
    flex: 0 0 50px;
    text-align: right;
}}

/* ---------------- AI synthesis block ---------------- */
.synthesis-block {{
    background: {CHARCOAL};
    padding: 40px 44px;
    margin: 8px 0 0 0;
}}

.synthesis-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {BOSCH_RED};
    margin-bottom: 16px;
}}

.synthesis-quote {{
    font-family: {FONT_DISPLAY};
    font-size: 21px;
    line-height: 1.5;
    font-weight: 600;
    color: #FFFFFF;
    max-width: 780px;
}}

.synthesis-grid {{
    display: flex;
    gap: 40px;
    margin-top: 28px;
    padding-top: 22px;
    border-top: 1px solid rgba(255,255,255,0.12);
}}

.synthesis-grid .s-col {{ flex: 1; }}

.synthesis-grid .s-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 6px;
}}

.synthesis-grid .s-value {{
    font-size: 13.5px;
    color: rgba(255,255,255,0.85);
    line-height: 1.5;
}}

/* ---------------- Stepper (Generate workflow) ---------------- */
.step-block {{
    display: flex;
    gap: 22px;
    padding: 22px 0;
    border-bottom: 1px solid {HAIRLINE};
}}

.step-num {{
    font-family: {FONT_DISPLAY};
    font-size: 13px;
    font-weight: 800;
    color: {SLATE};
    flex: 0 0 32px;
    padding-top: 3px;
}}

.step-num.active {{ color: {BOSCH_RED}; }}

.step-heading {{
    font-family: {FONT_DISPLAY};
    font-size: 16px;
    font-weight: 800;
    color: {GRAPHITE};
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}}

.step-desc {{
    font-size: 12.5px;
    color: {SLATE};
    margin-bottom: 14px;
}}

/* ---------------- Generation progress ---------------- */
.progress-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 0;
    font-size: 14px;
    color: {SLATE};
    border-bottom: 1px solid {HAIRLINE};
}}

.progress-row.done {{ color: {GRAPHITE}; font-weight: 600; }}
.progress-row.active {{ color: {BOSCH_RED}; font-weight: 700; }}

.progress-mark {{
    width: 18px; height: 18px;
    flex-shrink: 0;
    border-radius: 50%;
    border: 1.5px solid {HAIRLINE_STRONG};
    display: flex; align-items: center; justify-content: center;
    font-size: 10px;
}}

.progress-row.done .progress-mark {{
    background: {GRAPHITE};
    border-color: {GRAPHITE};
    color: #fff;
}}

.progress-row.active .progress-mark {{
    border-color: {BOSCH_RED};
    color: {BOSCH_RED};
}}

/* ---------------- Timeline (activity) ---------------- */
.tl-row {{
    display: flex;
    gap: 20px;
    padding: 14px 0;
    border-bottom: 1px solid {HAIRLINE};
}}

.tl-time {{
    font-family: {FONT_DISPLAY};
    font-size: 12px;
    font-weight: 700;
    color: {SLATE};
    flex: 0 0 64px;
    padding-top: 2px;
}}

.tl-line {{
    flex: 0 0 1px;
    background: {HAIRLINE_STRONG};
}}

.tl-event {{
    font-size: 13.5px;
    font-weight: 700;
    color: {GRAPHITE};
}}

.tl-detail {{
    font-size: 12.5px;
    color: {SLATE};
    margin-top: 2px;
}}

/* ---------------- Editorial empty state ---------------- */
.empty-state {{
    padding: 64px 40px;
    text-align: center;
    background: {PAPER};
    border: 1px dashed {HAIRLINE_STRONG};
}}

.empty-eyebrow {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {BOSCH_RED};
    margin-bottom: 12px;
}}

.empty-title {{
    font-family: {FONT_DISPLAY};
    font-size: 22px;
    font-weight: 800;
    color: {GRAPHITE};
    max-width: 480px;
    margin: 0 auto 10px auto;
}}

.empty-sub {{
    font-size: 13.5px;
    color: {SLATE};
    max-width: 420px;
    margin: 0 auto;
}}

/* ---------------- Metric strip ---------------- */
.metric-strip {{
    display: flex;
    border-top: 1px solid {HAIRLINE_STRONG};
    border-bottom: 1px solid {HAIRLINE_STRONG};
    margin: 8px 0 0 0;
}}

.metric-cell {{
    flex: 1;
    padding: 20px 24px;
    border-right: 1px solid {HAIRLINE};
}}

.metric-cell:last-child {{ border-right: none; }}

.metric-cell .m-label {{
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {SLATE};
}}

.metric-cell .m-value {{
    font-family: {FONT_DISPLAY};
    font-size: 28px;
    font-weight: 800;
    color: {GRAPHITE};
    margin-top: 6px;
}}

.metric-cell .m-sub {{
    font-size: 11.5px;
    color: {SLATE};
    margin-top: 2px;
}}

/* ---------------- Report library rows ---------------- */
.report-row {{
    display: flex;
    gap: 24px;
    padding: 22px 0;
    border-bottom: 1px solid {HAIRLINE};
}}

.report-thumb {{
    flex: 0 0 120px;
    height: 84px;
    background: {CHARCOAL};
    overflow: hidden;
}}

.report-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}

.report-info {{ flex: 1; }}

.report-week {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {BOSCH_RED};
    text-transform: uppercase;
}}

.report-title {{
    font-family: {FONT_DISPLAY};
    font-size: 17px;
    font-weight: 800;
    color: {GRAPHITE};
    margin-top: 4px;
}}

.report-sub {{
    font-size: 12.5px;
    color: {SLATE};
    margin-top: 4px;
}}

/* ---------------- Visual library grid ---------------- */
.vis-caption {{
    font-size: 11.5px;
    color: {SLATE};
    margin-top: 6px;
    line-height: 1.4;
}}

.vis-caption b {{ color: {GRAPHITE}; }}

/* ---------------- Buttons ---------------- */
.stButton > button {{
    background: {GRAPHITE};
    color: #FFFFFF;
    border: none;
    border-radius: 2px;
    height: 46px;
    font-size: 13.5px;
    font-weight: 700;
    letter-spacing: 0.3px;
    width: 100%;
    transition: background .15s ease, transform .1s ease;
}}

.stButton > button:hover {{
    background: {BOSCH_RED};
    transform: translateY(-1px);
}}
.stButton > button:active {{
    transform: translateY(0px) scale(0.98);
}}
.stButton > button:focus-visible {{
    outline: 2px solid {BOSCH_RED};
    outline-offset: 2px;
}}
.stButton > button:disabled {{
    background: {HAIRLINE_STRONG};
    color: {SLATE};
    transform: none;
    cursor: not-allowed;
}}

.stButton > button[kind="primary"] {{
    background: {BOSCH_RED};
}}
.stButton > button[kind="primary"]:hover {{
    background: {BOSCH_RED_DARK};
    transform: translateY(-1px);
}}

.stDownloadButton > button {{
    background: transparent;
    color: {GRAPHITE};
    border: 1.5px solid {GRAPHITE};
    border-radius: 2px;
    font-weight: 700;
    height: 46px;
    transition: background .15s ease, color .15s ease, transform .1s ease;
}}
.stDownloadButton > button:hover {{
    background: {GRAPHITE};
    color: #fff;
    transform: translateY(-1px);
}}
.stDownloadButton > button:active {{
    transform: translateY(0px) scale(0.98);
}}

/* ---------------- Tabs -- reactive underline ---------------- */
.stTabs [data-baseweb="tab"] {{
    transition: color .12s ease;
}}
.stTabs [data-baseweb="tab"]:hover p {{
    color: {BOSCH_RED} !important;
}}
.stTabs [aria-selected="true"] p {{
    color: {BOSCH_RED} !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: {BOSCH_RED} !important;
}}

/* ---------------- Multiselect chips -- reactive remove ---------------- */
div[data-baseweb="tag"] {{
    background: {GRAPHITE} !important;
    transition: background .12s ease;
}}
div[data-baseweb="tag"]:hover {{
    background: {BOSCH_RED} !important;
}}

/* ---------------- Inputs ---------------- */
.stTextInput input, .stTextArea textarea, .stDateInput input,
.stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {{
    border-radius: 2px !important;
    border-color: {HAIRLINE_STRONG} !important;
}}

div[data-testid="stExpander"] {{
    border: 1px solid {HAIRLINE};
    border-radius: 2px;
    background: {CARD};
}}

/* ---------------- Sidebar nav ---------------- */
.nav-brand {{
    padding: 28px 22px 20px 22px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}

.nav-brand-name {{
    font-family: {FONT_DISPLAY};
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #FFFFFF;
    margin-top: 12px;
}}

.nav-brand-sub {{
    font-size: 10.5px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-top: 2px;
}}

section[data-testid="stSidebar"] .stButton > button {{
    background: transparent;
    color: rgba(255,255,255,0.55);
    text-align: left;
    justify-content: flex-start;
    font-weight: 600;
    font-size: 13px;
    height: 42px;
    border-radius: 0;
    border-left: 2px solid transparent;
    padding-left: 22px;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.05);
    color: #FFFFFF;
    transform: none;
}}

section[data-testid="stSidebar"] div[class*="st-key-navactive_"] .stButton > button {{
    color: #FFFFFF;
    border-left: 2px solid {BOSCH_RED};
    background: rgba(226,0,26,0.08);
    font-weight: 700;
}}

/* ---------------- Floating feedback widget (kept, re-skinned) ---------------- */
div[class*="st-key-feedback_widget_fab"] {{
    position: fixed !important;
    right: 24px;
    bottom: 24px;
    z-index: 999999;
    width: 360px;
    max-width: calc(100vw - 48px);
}}

div[class*="st-key-feedback_widget_fab"] .stButton > button {{
    width: auto;
    height: 44px;
    padding: 0 20px;
    border-radius: 2px;
    float: right;
}}

div[class*="st-key-feedback_widget_fab"] div[data-testid="stLayoutWrapper"] div.stVerticalBlock {{
    background: {CARD} !important;
    border: 1px solid {HAIRLINE_STRONG};
    box-shadow: 0 24px 60px -20px rgba(20,20,22,0.35);
    padding: 20px 20px 12px 20px;
}}

/* ---------------- Footer credit ---------------- */
.workspace-footer {{
    margin-top: 48px;
    padding-top: 20px;
    border-top: 1px solid {HAIRLINE};
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: {SLATE};
}}

/* ---------------- Motion ---------------- */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.hero-zone, .brief-shell, .synthesis-block {{
    animation: fadeUp .5s cubic-bezier(.2,.8,.2,1);
}}
</style>
""".strip()
    st.markdown(css, unsafe_allow_html=True)
