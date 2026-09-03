class CategorizationAgent:
    """
    Scores every category against an article's title (and RSS summary,
    when available) by counting matched keywords, rather than a naive
    first-match loop. This fixes the "model" keyword swallowing almost
    everything into Large Language Models: a title that only weakly
    matches LLM (one broad keyword) but strongly matches a more specific
    category (multiple keyword hits) is now correctly routed to the
    specific category.

    Categories are still listed most-specific-first as a tie-breaker
    (used only when two categories have the exact same match count), but
    the primary signal is now match count, not dict iteration order.
    """

    CATEGORIES = {
        "Healthcare AI": [
            "health", "medical", "clinical", "diagnosis", "patient", "hospital", "drug discovery",
        ],
        "Robotics": [
            "robot", "robotics", "humanoid", "manipulation", "actuator", "autonomous vehicle",
        ],
        "Cybersecurity": [
            "security", "cyber", "vulnerability", "exploit", "breach", "malware", "threat detection",
        ],
        "AI Agents": [
            "agent", "agentic", "copilot", "autogen", "crewai", "multi-agent", "autonomous workflow",
        ],
        "AI Infrastructure": [
            "infrastructure", "datacenter", "data center", "cluster", "supercomputer", "networking fabric",
        ],
        "AI Hardware": [
            "gpu", "nvidia", "cuda", "chip", "accelerator", "tpu", "silicon", "semiconductor",
        ],
        "Cloud AI": [
            "azure", "aws", "google cloud", "vertex", "bedrock", "cloud platform", "managed service",
        ],
        "Computer Vision": [
            "computer vision", "image recognition", "object detection", "segmentation", "video understanding",
        ],
        "Speech AI": [
            "speech", "voice", "audio model", "text-to-speech", "transcription",
        ],
        "Developer AI": [
            "developer", "coding assistant", "code generation", "sdk", "api release", "ide",
        ],
        "Generative AI": [
            "generative", "diffusion", "text-to-image", "image generation", "video generation", "genai",
        ],
        "Large Language Models": [
            "gpt", "llm", "chatgpt", "claude", "gemini", "mistral", "llama", "language model", "model",
        ],
    }

    # Confidence below this falls back to "General AI" even if something
    # matched at all - a single weak keyword hit shouldn't be treated as
    # a confident classification.
    MIN_CONFIDENCE = 0.12

    def categorize(self, articles):

        for article in articles:

            haystack = article.title.lower()
            if getattr(article, "raw_content", ""):
                haystack += " " + article.raw_content.lower()

            best_category = "General AI"
            best_score = 0
            best_matches = 0

            for category, keywords in self.CATEGORIES.items():
                matches = sum(1 for kw in keywords if kw in haystack)
                if matches == 0:
                    continue

                # Longer/more-specific keyword phrases count for more than
                # single common words (e.g. "google cloud" > "model").
                weighted = sum(
                    (2 if " " in kw else 1)
                    for kw in keywords
                    if kw in haystack
                )

                if weighted > best_score:
                    best_score = weighted
                    best_category = category
                    best_matches = matches

            # Normalize into a rough 0-1 confidence: more matched keywords
            # (and longer/more specific ones) -> higher confidence.
            confidence = min(1.0, best_score / 4) if best_matches else 0.0

            if confidence < self.MIN_CONFIDENCE:
                article.category = "General AI"
                article.category_confidence = confidence
            else:
                article.category = best_category
                article.category_confidence = round(confidence, 2)

        return articles
