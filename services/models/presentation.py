class Presentation:
    """
    Presentation-layer model. Everything PowerPointAgent needs to render
    the full editorial deck (cover, executive overview, weekly signals,
    section dividers, topic slides, strategic takeaways, references).
    """

    def __init__(self):

        self.title = ""
        self.subtitle = ""
        self.generated_date = ""

        # Executive overview slide
        self.executive_summary = ""     # narrative paragraph
        self.exec_stats = {}            # {"Developments": "8", ...}
        self.exec_themes = []           # top category names

        # Weekly signals slide: list of dicts
        # {"headline": str, "explanation": str, "impact": "High"/"Medium"/"Low"}
        self.weekly_signals = []

        # Topic slides, grouped in render order. Each item is
        # {"category": str, "needs_divider": bool, "slides": [Slide, ...]}
        self.sections = []

        # Flat list of all topic slides in render order (kept for anything
        # that wants a simple flat view, e.g. total count / validation)
        self.slides = []

        # Strategic takeaways slide: list of dicts
        # {"signal": str, "implication": str, "action": str}
        self.strategic_takeaways = []

        self.references = []

    def add_slide(self, slide):
        self.slides.append(slide)
