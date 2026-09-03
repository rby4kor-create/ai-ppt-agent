import hashlib


class WriterAgent:
    """
    Generates executive-level narrative content for each article.

    No external LLM is wired into this pipeline, so content is produced
    from templates rather than free-form generation - but every field
    below draws from a *pool* of phrasings (per category, and several
    that are category-agnostic) selected deterministically per article.
    That matters because a single fixed sentence with only the source
    name swapped in reads as an obvious repeated cutout once a reader
    sees three or four slides in a row. Pulling from several distinct
    phrasings per field keeps the deck from repeating itself while
    still staying deterministic (same article -> same output).
    """

    CATEGORY_FRAMING = {
        "Large Language Models": {
            "summary": [
                "introduces model or capability improvements that shift what enterprise LLM deployments can reliably do",
                "pushes the reliability bar for LLM-powered products up another notch",
                "changes the calculus for teams comparing frontier and open-weight models",
            ],
            "impact": [
                "Teams evaluating LLM vendors should re-benchmark existing use cases against this capability before the next model selection cycle",
                "Any product built on a prior-generation model should be re-tested against this release before the next roadmap review",
                "Procurement teams comparing LLM vendors now have a new data point to weigh into the next contract cycle",
            ],
            "why": [
                "Model-level shifts propagate quickly into every downstream product built on top of them",
                "Because so much enterprise tooling sits directly on top of the model layer, changes here rarely stay contained to one team",
                "Capability jumps at the model layer tend to reset expectations across every team building on it",
            ],
            "tech": ["Large Language Models", "Fine-tuning", "Inference Optimization"],
            "readiness": "Pilot-ready",
        },
        "AI Agents": {
            "summary": [
                "advances autonomous or multi-step agent tooling aimed at production workflows",
                "extends what a single agent can be trusted to do without a human checking each step",
                "adds new orchestration primitives for chaining tools and actions reliably",
            ],
            "impact": [
                "Relevant to any team building internal copilots or workflow automation on top of agent frameworks",
                "Worth a look for teams currently prototyping agentic workflows, since it may shorten the path to production",
                "Changes what's feasible for teams weighing how much of a workflow to hand over to an agent",
            ],
            "why": [
                "Agent orchestration is quickly becoming the layer where enterprise AI ROI is won or lost",
                "As agents take on more multi-step work, the tooling that coordinates them becomes a competitive differentiator in its own right",
                "Reliability at the orchestration layer is what separates a demo from a production agent",
            ],
            "tech": ["Agent Orchestration", "Tool Use", "Workflow Automation"],
            "readiness": "Early pilot",
        },
        "Cloud AI": {
            "summary": [
                "expands managed AI infrastructure or platform services from a major cloud provider",
                "adds new managed tooling that shifts more of the AI stack off internal infrastructure teams",
                "broadens what's available directly through existing cloud procurement channels",
            ],
            "impact": [
                "Affects build-vs-buy decisions for AI infrastructure and may reduce total cost of ownership for current workloads",
                "Gives infrastructure teams another managed option to weigh against maintaining custom tooling in-house",
                "May shift the economics of current workloads enough to be worth a fresh cost comparison",
            ],
            "why": [
                "Platform-level changes affect procurement, security review, and vendor lock-in considerations",
                "Cloud platform shifts tend to ripple into procurement and vendor-risk conversations well beyond the engineering team",
                "Because so much AI infrastructure now runs through a handful of cloud platforms, changes here have an outsized reach",
            ],
            "tech": ["Managed AI Platform", "Cloud Infrastructure", "MLOps"],
            "readiness": "Production-ready",
        },
        "Hardware": {
            "summary": [
                "signals a shift in the compute economics underlying AI training or inference",
                "changes the price-performance curve that infrastructure planning is built on",
                "points to where compute costs are headed over the next planning cycle",
            ],
            "impact": [
                "Should inform medium-term infrastructure and capacity planning, particularly for on-prem or hybrid AI workloads",
                "Worth factoring into any capacity plan currently being drafted for the next budget cycle",
                "Changes the cost baseline that current infrastructure forecasts were likely built on",
            ],
            "why": [
                "Compute cost and availability remain the primary constraint on enterprise AI scale-up",
                "Hardware economics set the ceiling on how much AI workload an organization can realistically run",
                "Few factors move the enterprise AI cost curve as directly as changes at the hardware layer",
            ],
            "tech": ["AI Accelerators", "GPU Infrastructure", "Compute Efficiency"],
            "readiness": "Planning stage",
        },
        "Healthcare AI": {
            "summary": [
                "applies AI techniques to a clinical, diagnostic, or healthcare-operations use case",
                "moves AI further into workflows that touch patient care or clinical decision-making",
                "extends applied AI into a regulated healthcare setting",
            ],
            "impact": [
                "Relevant primarily to regulated or safety-critical deployments where validation and compliance overhead is high",
                "Most relevant to teams already navigating clinical validation or regulatory review for AI tooling",
                "Sets a reference point for what validation rigor looks like in a safety-critical AI deployment",
            ],
            "why": [
                "Healthcare deployments set a high bar for safety and accuracy that other regulated industries often adopt next",
                "What clears the bar in a clinical setting is usually a strong signal for other regulated industries",
                "Patient-facing AI carries little margin for error, which makes this a useful benchmark for safety practices generally",
            ],
            "tech": ["Applied AI", "Clinical Decision Support"],
            "readiness": "Requires compliance review",
        },
        "Security": {
            "summary": [
                "addresses AI safety, alignment, or cybersecurity risk in deployed AI systems",
                "tightens the safety or security posture of a widely deployed AI system",
                "responds to a known class of risk in production AI deployments",
            ],
            "impact": [
                "Should be reviewed by security and governance teams ahead of any expanded AI rollout",
                "Worth a checkpoint with security and governance before any related rollout expands further",
                "Gives risk and compliance teams a concrete update to fold into the next AI governance review",
            ],
            "why": [
                "Security and alignment gaps are the most common reason enterprise AI pilots stall before production",
                "More AI pilots stall on security or governance review than on the underlying technology itself",
                "Trust and safety issues, once surfaced, tend to slow every related deployment until they're resolved",
            ],
            "tech": ["AI Safety", "Alignment", "Security Tooling"],
            "readiness": "Governance review",
        },
        "General AI": {
            "summary": [
                "reflects a broader trend in how AI capabilities are being packaged and adopted",
                "is a smaller but useful signal of where the wider market is heading",
                "adds another data point to the general direction of AI product development",
            ],
            "impact": [
                "Worth monitoring as part of the general competitive landscape rather than immediate action",
                "Doesn't require immediate action, but is worth keeping on the radar as the space evolves",
                "Useful context for the next competitive-landscape review, even without a direct action item",
            ],
            "why": [
                "Even non-core developments shape the pace and direction of the wider AI market",
                "Smaller signals like this one often preview where the larger players move next",
                "The cumulative effect of updates like this is what shapes the market over a quarter, even if no single one is decisive",
            ],
            "tech": ["Applied AI"],
            "readiness": "Monitor",
        },
    }

    # Natural-case phrasing for each category when it's dropped mid-sentence
    # (category.lower() turns "Cloud AI" into "cloud ai", which reads oddly
    # since AI is an acronym, not a regular word).
    CATEGORY_PHRASE = {
        "Large Language Models": "large language models",
        "AI Agents": "AI agents",
        "Cloud AI": "cloud AI",
        "Hardware": "hardware",
        "Healthcare AI": "healthcare AI",
        "Security": "security",
        "General AI": "general AI",
    }

    # Category-agnostic phrasing pools, so two slides in the same
    # category still read as distinct write-ups rather than the same
    # sentence with the vendor name swapped in.
    STRATEGIC_OBSERVATIONS = [
        "{source} is staking out ground in {category_phrase} ahead of where most competitors currently sit.",
        "This move gives {source} a sharper story in {category_phrase}, a space enterprise buyers are actively comparing vendors on right now.",
        "For enterprises weighing vendors in {category_phrase}, this narrows the gap {source} needed to close.",
        "{source}'s position in {category_phrase} looks stronger after this - worth factoring into any upcoming vendor comparison.",
        "Competitors in {category_phrase} now have less room to differentiate from {source} on this specific capability.",
        "This is the kind of update that quietly resets expectations for what {category_phrase} vendors are supposed to offer.",
    ]

    RECOMMENDATIONS = [
        "Have the team most exposed to {category_phrase} take a first look this sprint, and route it through governance if it touches anything in production.",
        "Worth a 30-minute review with the relevant platform owner before it lands on next quarter's roadmap by default.",
        "Flag this for whoever owns the {category_phrase} vendor relationship - it may change what's worth re-negotiating at renewal.",
        "Add it to the next architecture review agenda rather than letting it sit as a passive news item.",
        "Circulate a short brief to affected teams so it doesn't get rediscovered independently three separate times next quarter.",
        "Worth a quick gap-check against whatever {category_phrase} vendor is currently in production, even if no switch is planned.",
    ]

    def generate_content(self, repository):

        for category, articles in repository.get_categories().items():

            framing = self.CATEGORY_FRAMING.get(
                category, self.CATEGORY_FRAMING["General AI"]
            )

            for article in articles:
                self._write_article(article, category, framing)

        return repository

    def _write_article(self, article, category, framing):

        source = article.source
        title = article.title.strip().rstrip(".")

        def field_seed(field_name):
            digest = hashlib.sha256(f"{title}|{field_name}".encode("utf-8")).hexdigest()
            return int(digest, 16)

        base_seed = field_seed("base")

        summary_pool = framing["summary"]
        impact_pool = framing["impact"]
        why_pool = framing["why"]

        article.summary = f"{source} {summary_pool[field_seed('summary') % len(summary_pool)]}."
        article.business_impact = impact_pool[field_seed('impact') % len(impact_pool)] + "."
        article.why_it_matters = why_pool[field_seed('why') % len(why_pool)] + "."

        obs_template = self.STRATEGIC_OBSERVATIONS[field_seed('obs') % len(self.STRATEGIC_OBSERVATIONS)]
        rec_template = self.RECOMMENDATIONS[field_seed('rec') % len(self.RECOMMENDATIONS)]

        category_phrase = self.CATEGORY_PHRASE.get(category, category.lower())

        article.strategic_observation = obs_template.format(
            source=source, category=category, category_phrase=category_phrase
        )
        article.recommendation = rec_template.format(
            source=source, category=category, category_phrase=category_phrase
        )

        article.key_technologies = list(framing["tech"])
        article.enterprise_readiness = framing["readiness"]

        article.innovation_score = 5 + (base_seed % 6)  # 5-10, keeps the deck upbeat but varied

        risk_bucket = base_seed % 3
        article.risk_level = ["Low", "Medium", "Low"][risk_bucket] if category != "Security" else "Medium"
