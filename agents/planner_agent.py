class PlannerAgent:

    def create_plan(self, topic):

        slides = [
            "Introduction",
            f"What is {topic}?",
            "Architecture",
            "Key Features",
            "Business Benefits",
            "Real-world Use Cases",
            "Challenges",
            "Future Trends",
            "Conclusion",
            "References"
        ]

        return {
            "title": topic,
            "slides": slides
        }