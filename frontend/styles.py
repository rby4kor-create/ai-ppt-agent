import streamlit as st

# ---------------------------------------------------------------------------
# NEW VISUAL SYSTEM -- "Aurora Editorial"
#
# Deliberately far from the old dark-navy / Bosch-red console look:
# a bright, airy, editorial surface (soft paper background, not black),
# a violet -> coral gradient as the single accent system, glass cards,
# soft elevation instead of hard borders, and a rounded, humanist type
# scale (Sora for display, Inter for body). Every color used anywhere
# in the app is defined once here so the whole product reskins from one
# file.
# ---------------------------------------------------------------------------

INK = "#161320"           # near-black text, warmer than pure black
INK_SOFT = "#4B4560"      # secondary text
MUTED = "#8B85A0"         # tertiary / captions
PAPER = "#F6F4FB"         # app background (soft lavender-white, not navy)
SURFACE = "#FFFFFF"       # card background
BORDER = "rgba(22,19,32,0.08)"
BORDER_STRONG = "rgba(22,19,32,0.14)"

VIOLET = "#6C4EF2"        # primary accent
VIOLET_DARK = "#4E33D6"
CORAL = "#FF6B5B"         # secondary accent (warmth, contrast)
MINT = "#17B890"          # success / positive
AMBER = "#F5A524"         # warning
DANGER = "#E5484D"

GRADIENT_PRIMARY = f"linear-gradient(120deg, {VIOLET} 0%, #9A7BFF 45%, {CORAL} 100%)"
GRADIENT_SOFT = "linear-gradient(135deg, rgba(108,78,242,0.10), rgba(255,107,91,0.08))"


def load_css():
    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: {PAPER};
    background-image:
        radial-gradient(circle at 8% 0%, rgba(108,78,242,0.10) 0%, transparent 42%),
        radial-gradient(circle at 95% 15%, rgba(255,107,91,0.10) 0%, transparent 40%);
    color: {INK};
}}

section[data-testid="stSidebar"] {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}

header {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}

h1, h2, h3 {{
    font-family: 'Sora', sans-serif;
    color: {INK};
}}

/* ---------- Hero ---------- */
.hero-shell {{
    background: {GRADIENT_PRIMARY};
    border-radius: 28px;
    padding: 40px 44px;
    margin-bottom: 28px;
    box-shadow: 0 20px 50px -20px rgba(108,78,242,0.55);
    position: relative;
    overflow: hidden;
}}

.hero-shell::after {{
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle at 85% 20%, rgba(255,255,255,0.25) 0%, transparent 55%);
}}

.eyebrow {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.85);
    text-transform: uppercase;
    margin-bottom: 10px;
    position: relative;
}}

.hero-title {{
    font-family: 'Sora', sans-serif;
    font-size: 40px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
    position: relative;
}}

.hero-sub {{
    font-size: 16px;
    color: rgba(255,255,255,0.92);
    max-width: 640px;
    margin-bottom: 0;
    position: relative;
}}

.hero-pills {{
    display: flex;
    gap: 10px;
    margin-top: 20px;
    flex-wrap: wrap;
    position: relative;
}}

.hero-pill {{
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.35);
    color: white;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 600;
    backdrop-filter: blur(6px);
}}

/* ---------- Section titles ---------- */
.section-title {{
    font-family: 'Sora', sans-serif;
    font-size: 21px;
    font-weight: 700;
    margin-top: 6px;
    margin-bottom: 14px;
    color: {INK};
    display: flex;
    align-items: center;
    gap: 10px;
}}

.section-title .dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {GRADIENT_PRIMARY};
    display: inline-block;
}}

/* ---------- Buttons ---------- */
.stButton > button {{
    background: {GRADIENT_PRIMARY};
    color: white;
    border: none;
    border-radius: 14px;
    height: 52px;
    font-size: 15.5px;
    font-weight: 700;
    width: 100%;
    box-shadow: 0 10px 24px -10px rgba(108,78,242,0.55);
    transition: transform .12s ease, box-shadow .12s ease;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 14px 28px -10px rgba(108,78,242,0.65);
}}

.stDownloadButton > button {{
    background: {INK};
    color: white;
    border-radius: 14px;
    font-weight: 700;
    height: 52px;
}}

/* ---------- Cards ---------- */
.glass-card {{
    background: {SURFACE};
    border-radius: 18px;
    padding: 22px 22px;
    border: 1px solid {BORDER};
    box-shadow: 0 12px 30px -18px rgba(22,19,32,0.18);
    height: 100%;
}}

.metric-card {{
    background: {SURFACE};
    border-radius: 18px;
    padding: 22px;
    border: 1px solid {BORDER};
    box-shadow: 0 12px 30px -18px rgba(22,19,32,0.15);
    height: 148px;
    position: relative;
    overflow: hidden;
}}

.metric-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: {GRADIENT_PRIMARY};
}}

.metric-label {{
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {MUTED};
    text-transform: uppercase;
}}

.metric-value {{
    font-family: 'Sora', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: {INK};
    margin-top: 8px;
}}

.metric-sub {{
    font-size: 12.5px;
    color: {MUTED};
    margin-top: 4px;
}}

.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .3px;
}}

.badge-ok {{ background: rgba(23,184,144,0.14); color: {MINT}; }}
.badge-warn {{ background: rgba(245,165,36,0.16); color: {AMBER}; }}
.badge-info {{ background: rgba(108,78,242,0.12); color: {VIOLET_DARK}; }}
.badge-danger {{ background: rgba(229,72,77,0.14); color: {DANGER}; }}

/* ---------- Step checklist ---------- */
.step-row {{
    display: flex;
    align-items: center;
    padding: 9px 12px;
    font-size: 14px;
    color: {MUTED};
    border-radius: 10px;
    margin-bottom: 4px;
    background: transparent;
    transition: background .15s ease;
}}

.step-row.done {{
    color: {INK};
    background: {GRADIENT_SOFT};
    font-weight: 600;
}}

.step-mark {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    margin-right: 12px;
    font-size: 11px;
    font-weight: 800;
    background: {BORDER};
    color: {MUTED};
}}

.step-row.done .step-mark {{
    background: {GRADIENT_PRIMARY};
    color: white;
}}

/* ---------- Misc ---------- */
hr {{ border-color: {BORDER} !important; }}

div[data-testid="stExpander"] {{
    border: 1px solid {BORDER};
    border-radius: 14px;
    background: {SURFACE};
}}

.stTextInput input, .stTextArea textarea, .stDateInput input {{
    border-radius: 10px !important;
}}

/* ---------- Activity log ---------- */
.log-line {{
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 12.5px;
    padding: 8px 12px;
    border-radius: 10px;
    border: 1px solid {BORDER};
    margin-bottom: 6px;
    background: {SURFACE};
    display: flex;
    gap: 12px;
    align-items: baseline;
}}

.log-time {{ color: {MUTED}; white-space: nowrap; }}
.log-event {{ font-weight: 700; color: {VIOLET_DARK}; white-space: nowrap; }}
.log-detail {{ color: {INK_SOFT}; }}

/* ---------- Floating feedback widget ----------
   st.container(key="feedback_widget_fab") renders as a real wrapping
   div carrying this class -- unlike a plain st.markdown div, it
   actually contains the button/card rendered inside the `with` block,
   so pinning IT to the viewport corner genuinely floats the widget. */
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
    height: 48px;
    padding: 0 22px;
    border-radius: 999px;
    box-shadow: 0 14px 30px -10px rgba(108,78,242,0.55);
    float: right;
}}

/* The inner `with st.container(border=True)` block renders as a nested
   stVerticalBlock one level down, with no background of its own (it
   inherits the transparent app background) -- without an explicit
   opaque fill here, whatever is fixed *underneath* on the page shows
   straight through the "floating" card. */
div[class*="st-key-feedback_widget_fab"] div[data-testid="stLayoutWrapper"] div.stVerticalBlock {{
    background: {SURFACE} !important;
    border-radius: 18px !important;
    box-shadow: 0 20px 50px -16px rgba(22,19,32,0.35);
    padding: 20px 20px 12px 20px;
}}
</style>
""".strip()

    st.markdown(css, unsafe_allow_html=True)
