class ExecutiveSummaryAgent:
    """
    Generates the one-paragraph executive narrative for the "This Week at
    a Glance" slide, from the actual set of ExecutiveAnalysis objects
    that made the cut - referencing real counts and the top domain by
    volume, rather than a fully generic paragraph.
    """

    def generate_summary(self, analyses):

        if not analyses:
            return "No qualifying AI developments were identified for this reporting period."

        categories = {}
        for a in analyses:
            categories[a.category] = categories.get(a.category, 0) + 1

        top_category = max(categories, key=categories.get)
        avg_innovation = sum(a.innovation_score for a in analyses) / len(analyses)

        return (
            f"This week's report covers {len(analyses)} enterprise-relevant AI developments "
            f"across {len(categories)} technology domains, with {top_category} accounting for "
            f"the largest share of activity. Average innovation across selected developments "
            f"scored {avg_innovation:.1f}/10, reflecting a week of continued, if uneven, "
            f"progress toward production-ready enterprise AI capability."
        )
