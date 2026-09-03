from services.llm_service import LLMService


class ImagePromptAgent:

    def __init__(self):
        self.llm = LLMService()

    def generate_prompt(
        self,
        article,
        analysis
    ):
        return self.llm.generate_image_prompt(
            article,
            analysis
        )
        return prompt.strip()