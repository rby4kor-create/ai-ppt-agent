class Slide:
    """
    Presentation-layer model for a single topic slide. Built by
    PresentationBuilder from an ExecutiveAnalysis object. PowerPointAgent
    only ever reads from Slide/Presentation - it has no knowledge of
    Article or ExecutiveAnalysis, keeping the renderer decoupled from the
    content pipeline.
    """

    def __init__(self):

        # Header
        self.category = ""

        # Main title (may be shortened for display; full title preserved
        # via source_title for the references slide)
        self.title = ""
        self.source_title = ""

        # 3 "why it matters" bullets
        self.summary = []

        # Enterprise Intelligence block
        self.strategic_observation = ""   # from ExecutiveAnalysis.strategic_importance
        self.recommendation = ""          # from ExecutiveAnalysis.enterprise_recommendation

        # Executive scorecard
        self.key_technologies = []
        self.innovation_score = 0         # 0-10
        self.risk_level = "Low"           # Low / Medium / High
        self.enterprise_readiness = ""    # display label, e.g. "Pilot-ready"

        # Image resolution (set by PresentationBuilder via ImageAgent)
        self.image_path = ""

        # Category, used to pick the fallback illustration asset
        self.visual_type = ""

        # Source
        self.source = ""
        self.source_link = ""

        # Speaker notes
        self.notes = ""

        # Slide number (within the topic-slide sequence, not the absolute
        # deck page number)
        self.slide_number = 0
