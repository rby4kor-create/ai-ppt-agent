import hashlib

from config import USE_LLM, OPENROUTER_MODEL
from models.executive_analysis import ExecutiveAnalysis
from utils.logger import get_logger

logger = get_logger(__name__)


class TemplateAnalysisAgent:
    """
    Deterministic, offline analysis generator. Used when USE_LLM is False,
    no OPENROUTER_API_KEY is configured, or an individual LLM call fails
    after retries - so the pipeline always produces a complete,
    schema-valid ExecutiveAnalysis for every selected article, never a
    missing slide.

    Every field draws from a *pool* of phrasings (per category, plus
    several category-agnostic pools) selected deterministically per
    article via a title-derived hash, so consecutive slides in the same
    category don't read as the same sentence with the vendor swapped in.
    This is a template, not real analysis - it is explicitly a fallback,
    not a substitute for LLM grounding, and ExecutiveAnalysis.generated_by
    is set to "template" so this is traceable in logs/QA.
    """

    CATEGORY_FRAMING = {
        "Large Language Models": {
            "summary": [
                "introduces model or capability improvements that shift what enterprise LLM deployments can reliably do",
                "pushes the reliability bar for LLM-powered products up another notch",
                "changes the calculus for teams comparing frontier and open-weight models",
            ],
            "impact": [
                "Teams evaluating LLM vendors should re-benchmark existing use cases against this capability before the next selection cycle.",
                "Any product built on a prior-generation model should be re-tested against this release before the next roadmap review.",
                "Procurement teams comparing LLM vendors now have a new data point for the next contract cycle.",
            ],
            "why": [
                "Model-level shifts propagate quickly into every downstream product built on top of them.",
                "Because so much enterprise tooling sits directly on the model layer, changes here rarely stay contained to one team.",
                "Capability jumps at the model layer tend to reset expectations across every team building on it.",
            ],
            "tech": ["Large Language Models", "Fine-tuning", "Inference Optimization"],
            "readiness_label": "Pilot-ready", "readiness_score": 7,
        },
        "AI Agents": {
            "summary": [
                "advances autonomous or multi-step agent tooling aimed at production workflows",
                "extends what a single agent can be trusted to do without a human checking each step",
                "adds new orchestration primitives for chaining tools and actions reliably",
            ],
            "impact": [
                "Relevant to any team building internal copilots or workflow automation on agent frameworks.",
                "Worth a look for teams prototyping agentic workflows - it may shorten the path to production.",
                "Changes what's feasible for teams weighing how much of a workflow to hand to an agent.",
            ],
            "why": [
                "Agent orchestration is quickly becoming the layer where enterprise AI ROI is won or lost.",
                "As agents take on more multi-step work, coordination tooling becomes a differentiator in its own right.",
                "Reliability at the orchestration layer is what separates a demo from a production agent.",
            ],
            "tech": ["Agent Orchestration", "Tool Use", "Workflow Automation"],
            "readiness_label": "Early pilot", "readiness_score": 5,
        },
        "Cloud AI": {
            "summary": [
                "expands managed AI infrastructure or platform services from a major cloud provider",
                "adds managed tooling that shifts more of the AI stack off internal infrastructure teams",
                "broadens what's available directly through existing cloud procurement channels",
            ],
            "impact": [
                "Affects build-vs-buy decisions for AI infrastructure and may reduce total cost of ownership.",
                "Gives infrastructure teams another managed option to weigh against custom in-house tooling.",
                "May shift the economics of current workloads enough to justify a fresh cost comparison.",
            ],
            "why": [
                "Platform-level changes affect procurement, security review, and vendor lock-in considerations.",
                "Cloud platform shifts tend to ripple into procurement and vendor-risk conversations beyond engineering.",
                "Because so much AI infrastructure runs through a handful of cloud platforms, changes here reach far.",
            ],
            "tech": ["Managed AI Platform", "Cloud Infrastructure", "MLOps"],
            "readiness_label": "Production-ready", "readiness_score": 9,
        },
        "AI Hardware": {
            "summary": [
                "signals a shift in the compute economics underlying AI training or inference",
                "changes the price-performance curve that infrastructure planning is built on",
                "points to where compute costs are headed over the next planning cycle",
            ],
            "impact": [
                "Should inform medium-term infrastructure and capacity planning, particularly for hybrid workloads.",
                "Worth factoring into any capacity plan currently being drafted for the next budget cycle.",
                "Changes the cost baseline that current infrastructure forecasts were likely built on.",
            ],
            "why": [
                "Compute cost and availability remain the primary constraint on enterprise AI scale-up.",
                "Hardware economics set the ceiling on how much AI workload an organization can realistically run.",
                "Few factors move the enterprise AI cost curve as directly as changes at the hardware layer.",
            ],
            "tech": ["AI Accelerators", "GPU Infrastructure", "Compute Efficiency"],
            "readiness_label": "Planning stage", "readiness_score": 4,
        },
        "AI Infrastructure": {
            "summary": [
                "expands the underlying compute, networking, or datacenter capacity available for AI workloads",
                "addresses a scaling bottleneck that has been constraining larger AI training runs",
                "changes what's operationally possible at the infrastructure layer for AI workloads",
            ],
            "impact": [
                "Relevant to teams planning multi-quarter capacity or datacenter commitments.",
                "Worth reviewing against current infrastructure roadmaps before the next capacity decision.",
                "Changes the assumptions behind current large-scale training or serving plans.",
            ],
            "why": [
                "Infrastructure constraints, not model ideas, are increasingly the limiting factor on AI scale-up.",
                "Every layer above infrastructure inherits its limits, so changes here ripple broadly.",
                "Capacity and networking decisions made now shape what's possible for years, not quarters.",
            ],
            "tech": ["AI Infrastructure", "Datacenter Scaling", "Networking Fabric"],
            "readiness_label": "Planning stage", "readiness_score": 4,
        },
        "Robotics": {
            "summary": [
                "advances physical-world AI capability in manipulation, navigation, or autonomous operation",
                "reduces the cost or complexity of collecting the data robotics models depend on",
                "moves a robotics capability closer to reliable, repeatable real-world deployment",
            ],
            "impact": [
                "Relevant to any team evaluating automation for physical operations or logistics.",
                "Worth tracking if physical-world automation is anywhere on the current roadmap.",
                "Changes the near-term feasibility case for a physical automation pilot.",
            ],
            "why": [
                "Robotics has historically lagged software AI on reliability - closing that gap changes deployment timelines.",
                "Physical-world deployments carry safety and liability considerations that move slower than software.",
                "Data availability, not model architecture, has been the main constraint on robotics progress.",
            ],
            "tech": ["Robotics", "Manipulation", "Autonomous Systems"],
            "readiness_label": "Early pilot", "readiness_score": 4,
        },
        "Cybersecurity": {
            "summary": [
                "addresses AI safety, alignment, or cybersecurity risk in deployed AI systems",
                "tightens the safety or security posture of a widely deployed AI system",
                "responds to a known class of risk in production AI deployments",
            ],
            "impact": [
                "Should be reviewed by security and governance teams ahead of any expanded AI rollout.",
                "Worth a checkpoint with security and governance before any related rollout expands further.",
                "Gives risk and compliance teams a concrete update for the next AI governance review.",
            ],
            "why": [
                "Security and alignment gaps are the most common reason enterprise AI pilots stall before production.",
                "More AI pilots stall on security or governance review than on the underlying technology.",
                "Trust and safety issues, once surfaced, tend to slow every related deployment until resolved.",
            ],
            "tech": ["AI Safety", "Alignment", "Security Tooling"],
            "readiness_label": "Governance review", "readiness_score": 5,
        },
        "Healthcare AI": {
            "summary": [
                "applies AI techniques to a clinical, diagnostic, or healthcare-operations use case",
                "moves AI further into workflows that touch patient care or clinical decision-making",
                "extends applied AI into a regulated healthcare setting",
            ],
            "impact": [
                "Relevant primarily to regulated or safety-critical deployments with high validation overhead.",
                "Most relevant to teams already navigating clinical validation or regulatory review.",
                "Sets a reference point for validation rigor in safety-critical AI deployment.",
            ],
            "why": [
                "Healthcare deployments set a high bar for safety that other regulated industries often adopt next.",
                "What clears the bar in a clinical setting is usually a strong signal for other regulated industries.",
                "Patient-facing AI carries little margin for error, making this a useful safety benchmark generally.",
            ],
            "tech": ["Applied AI", "Clinical Decision Support"],
            "readiness_label": "Requires compliance review", "readiness_score": 3,
        },
        "Computer Vision": {
            "summary": [
                "improves visual recognition, detection, or understanding capability for real-world imagery",
                "extends what automated visual inspection or analysis can reliably catch",
                "narrows the gap between lab-grade and production-grade computer vision accuracy",
            ],
            "impact": [
                "Relevant to any workflow involving visual inspection, quality control, or media analysis.",
                "Worth evaluating against current vision pipelines before the next model refresh.",
                "May reduce false-negative rates in existing detection workflows.",
            ],
            "why": [
                "Vision accuracy gains compound quickly across inspection, safety, and content workflows.",
                "Small accuracy gains in vision systems often translate directly into fewer manual review hours.",
                "Vision is one of the few AI domains with a direct, measurable production accuracy bar.",
            ],
            "tech": ["Computer Vision", "Object Detection", "Visual QA"],
            "readiness_label": "Pilot-ready", "readiness_score": 6,
        },
        "Speech AI": {
            "summary": [
                "improves speech recognition, synthesis, or audio understanding capability",
                "extends what voice-driven interfaces or transcription pipelines can reliably do",
                "narrows the latency or accuracy gap for real-time voice applications",
            ],
            "impact": [
                "Relevant to teams building voice interfaces, transcription, or call-center automation.",
                "Worth benchmarking against current speech pipelines before the next vendor review.",
                "May change the cost/accuracy tradeoff for existing transcription workloads.",
            ],
            "why": [
                "Voice interfaces are becoming a default enterprise UX layer, not a niche feature.",
                "Accuracy and latency gains in speech directly affect customer-facing experience quality.",
                "Speech pipelines are often the least-reviewed part of an AI stack despite heavy usage.",
            ],
            "tech": ["Speech AI", "Voice Interfaces", "Transcription"],
            "readiness_label": "Pilot-ready", "readiness_score": 6,
        },
        "Developer AI": {
            "summary": [
                "extends AI-assisted software development tooling for enterprise engineering teams",
                "changes what a coding assistant can reliably automate versus merely suggest",
                "adds new developer-facing tooling that shortens the build-to-ship cycle",
            ],
            "impact": [
                "Relevant to engineering leadership evaluating AI coding assistants at scale.",
                "Worth a pilot with a small engineering team before a broader tooling decision.",
                "May change the calculus on current developer-tooling vendor agreements.",
            ],
            "why": [
                "Developer tooling adoption tends to spread organically once one team sees clear productivity gains.",
                "Code-quality and security implications of AI-assisted development are still an active governance topic.",
                "Engineering velocity gains here compound across every team that adopts the tooling.",
            ],
            "tech": ["Developer AI", "Coding Assistants", "SDKs"],
            "readiness_label": "Pilot-ready", "readiness_score": 6,
        },
        "Generative AI": {
            "summary": [
                "advances generative model capability for image, video, or multimodal content",
                "narrows the quality gap between generated and production-grade creative content",
                "extends what generative tooling can reliably produce without heavy manual cleanup",
            ],
            "impact": [
                "Relevant to marketing, design, and content teams evaluating generative tooling.",
                "Worth reviewing IP and provenance implications before any production content use.",
                "May change build-vs-license decisions for creative/content tooling.",
            ],
            "why": [
                "Generative content quality gains directly affect production timelines for creative teams.",
                "IP, provenance, and brand-safety questions make generative AI a governance topic, not just a tooling one.",
                "Adoption in creative workflows tends to be fast once quality clears a usability bar.",
            ],
            "tech": ["Generative AI", "Diffusion Models", "Multimodal AI"],
            "readiness_label": "Pilot-ready", "readiness_score": 6,
        },
        "General AI": {
            "summary": [
                "reflects a broader trend in how AI capabilities are being packaged and adopted",
                "is a smaller but useful signal of where the wider market is heading",
                "adds another data point to the general direction of AI product development",
            ],
            "impact": [
                "Worth monitoring as part of the general competitive landscape rather than immediate action.",
                "Doesn't require immediate action, but is worth keeping on the radar as the space evolves.",
                "Useful context for the next competitive-landscape review, even without a direct action item.",
            ],
            "why": [
                "Even non-core developments shape the pace and direction of the wider AI market.",
                "Smaller signals like this one often preview where larger players move next.",
                "The cumulative effect of updates like this shapes the market over a quarter.",
            ],
            "tech": ["Applied AI"],
            "readiness_label": "Monitor", "readiness_score": 2,
        },
    }

    CATEGORY_PHRASE = {
        "Large Language Models": "large language models", "AI Agents": "AI agents",
        "Cloud AI": "cloud AI", "AI Hardware": "hardware", "AI Infrastructure": "AI infrastructure",
        "Robotics": "robotics", "Cybersecurity": "security", "Healthcare AI": "healthcare AI",
        "Computer Vision": "computer vision", "Speech AI": "speech AI", "Developer AI": "developer AI",
        "Generative AI": "generative AI", "General AI": "general AI",
    }

    STRATEGIC_OBSERVATIONS = [
        "{source} is staking out ground in {category_phrase} ahead of where most competitors currently sit.",
        "This move gives {source} a sharper story in {category_phrase}, a space buyers are actively comparing vendors on.",
        "For enterprises weighing vendors in {category_phrase}, this narrows the gap {source} needed to close.",
        "{source}'s position in {category_phrase} looks stronger after this - worth a vendor comparison.",
        "Competitors in {category_phrase} now have less room to differentiate from {source} on this capability.",
        "This quietly resets expectations for what {category_phrase} vendors are supposed to offer.",
    ]

    RECOMMENDATIONS = [
        "Have the team most exposed to {category_phrase} take a first look this sprint; route through governance if production-facing.",
        "Worth a 30-minute review with the relevant platform owner before it lands on next quarter's roadmap by default.",
        "Flag this for whoever owns the {category_phrase} vendor relationship - it may affect renewal terms.",
        "Add it to the next architecture review agenda rather than letting it sit as a passive news item.",
        "Circulate a short brief to affected teams so it isn't rediscovered independently next quarter.",
        "Worth a quick gap-check against whatever {category_phrase} vendor is currently in production.",
    ]

    FUTURE_OUTLOOK = [
        "Expect competitors in {category_phrase} to respond within one to two quarters.",
        "This is likely the first of several similar moves from {source} and its peers this year.",
        "Watch for follow-on announcements narrowing this gap further over the next few releases.",
    ]

    OPPORTUNITIES = [
        "Early mover advantage for teams that evaluate this before it becomes standard.",
        "Potential to reduce cost or engineering effort on an existing workflow.",
        "A concrete talking point for the next vendor or budget conversation.",
    ]

    RISKS = [
        "Vendor lock-in if adopted before alternatives are evaluated.",
        "Governance and compliance review may be needed before production use.",
        "Capability claims should be independently verified before roadmap commitments.",
    ]

    def generate(self, article) -> ExecutiveAnalysis:
        category = article.category or "General AI"
        framing = self.CATEGORY_FRAMING.get(category, self.CATEGORY_FRAMING["General AI"])
        source = article.source
        title = article.title.strip().rstrip(".")
        category_phrase = self.CATEGORY_PHRASE.get(category, category.lower())

        def pick(pool, field_name):
            digest = hashlib.sha256(f"{title}|{field_name}".encode("utf-8")).hexdigest()
            return pool[int(digest, 16) % len(pool)]

        def seed(field_name):
            digest = hashlib.sha256(f"{title}|{field_name}".encode("utf-8")).hexdigest()
            return int(digest, 16)

        executive_summary = f"{source} {pick(framing['summary'], 'summary')}."
        business_impact = pick(framing["impact"], "impact")
        strategic_importance = pick(self.STRATEGIC_OBSERVATIONS, "obs").format(
            source=source, category_phrase=category_phrase
        )
        recommendation = pick(self.RECOMMENDATIONS, "rec").format(
            source=source, category_phrase=category_phrase
        )
        future_outlook = pick(self.FUTURE_OUTLOOK, "outlook").format(
            source=source, category_phrase=category_phrase
        )
        technical_analysis = pick(framing["why"], "why")

        base_seed = seed("base")
        innovation_score = 5 + (base_seed % 6)  # 5-10
        risk_bucket = base_seed % 3
        risk_level = ["Low", "Medium", "Low"][risk_bucket] if category != "Cybersecurity" else "Medium"

        return ExecutiveAnalysis(
            title=article.title,
            category=category,
            source=source,
            article_url=article.link,
            published=article.published,
            executive_summary=executive_summary,
            business_impact=business_impact,
            technical_analysis=technical_analysis,
            enterprise_recommendation=recommendation,
            future_outlook=future_outlook,
            strategic_importance=strategic_importance,
            innovation_score=innovation_score,
            enterprise_readiness=framing["readiness_score"],
            confidence_score=0.55,  # template output; deliberately below LLM-typical confidence
            risk_level=risk_level,
            implementation_effort="Medium",
            key_takeaways=[business_impact],
            key_technologies=list(framing["tech"]),
            keywords=list(framing["tech"]),
            industry_impact=[framing["readiness_label"]],
            opportunities=[pick(self.OPPORTUNITIES, "opp")],
            risks=[pick(self.RISKS, "risk")],
            generated_by="template",
        )


class AnalysisAgent:
    """
    Orchestrates per-article analysis: tries the LLM (if enabled and
    configured) and falls back to TemplateAnalysisAgent per article on
    any failure, so a single bad LLM call never drops an article from
    the deck. Returns (analyses, diagnostics) where diagnostics reports
    exactly how many articles were LLM-analyzed vs. template-fallback vs.
    skipped, per Problem 2's diagnostic requirements.
    """

    def __init__(self, llm_service=None):
        self.template_agent = TemplateAnalysisAgent()
        self._llm_service = llm_service
        self._llm_init_failed = False

    def _get_llm_service(self):
        if self._llm_service is not None:
            return self._llm_service
        if self._llm_init_failed:
            return None
        try:
            from services.llm_service import LLMService
            self._llm_service = LLMService()
            return self._llm_service
        except Exception as e:
            logger.warning(f"LLM service unavailable, using template fallback for all articles: {e}")
            self._llm_init_failed = True
            return None

    def analyze(self, articles):
        analyses = []
        diagnostics = {"llm": 0, "template_fallback": 0, "skipped": []}

        import os
        api_key = os.environ.get("OPENROUTER_API_KEY")
        llm_enabled = USE_LLM and bool(api_key)

        if not USE_LLM:
            logger.warning(
                "LLM analysis is OFF (USE_LLM=False in config.py). "
                "Every article will use the deterministic template fallback."
            )
        elif not api_key:
            logger.warning(
                "=" * 70 + "\n"
                "LLM analysis is ENABLED (USE_LLM=True) but OPENROUTER_API_KEY "
                "was not found in the environment.\n"
                "Every article will silently use the deterministic template "
                "fallback instead of real analysis - this is almost certainly "
                "NOT what you want.\n"
                "Fix: put OPENROUTER_API_KEY=sk-... in a .env file in the "
                "project root (config.py now calls load_dotenv() to read it), "
                "or export it in your shell before running.\n" + "=" * 70
            )
        else:
            logger.info(f"LLM analysis is ENABLED - using model '{OPENROUTER_MODEL}'")

        llm = self._get_llm_service() if llm_enabled else None

        for article in articles:
            analysis = None

            if llm is not None:
                try:
                    analysis = llm.generate_analysis(article, article.raw_content)
                    diagnostics["llm"] += 1
                except Exception as e:
                    logger.warning(
                        f"LLM analysis failed for '{article.title[:60]}': {e} - "
                        f"falling back to template."
                    )

            if analysis is None:
                try:
                    analysis = self.template_agent.generate(article)
                    diagnostics["template_fallback"] += 1
                except Exception as e:
                    logger.error(f"Template analysis failed for '{article.title[:60]}': {e}")
                    diagnostics["skipped"].append({
                        "title": article.title, "source": article.source,
                        "reason": f"template generation error: {e}",
                    })
                    continue

            valid, reason = analysis.is_valid()
            if not valid:
                logger.warning(f"Dropping invalid analysis for '{article.title[:60]}': {reason}")
                diagnostics["skipped"].append({
                    "title": article.title, "source": article.source, "reason": reason,
                })
                continue

            analyses.append(analysis)

        return analyses, diagnostics
