import json
import re


class PromptAgent:

    def parse_prompt(self, prompt: str):

        week = re.search(r'CW(\d+)', prompt, re.IGNORECASE)

        data = {
            "report_type": "Weekly GenAI Technology Advances",
            "calendar_week": int(week.group(1)) if week else None,
            "year": 2026,
            "topics": 8,
            "include_images": True,
            "output_format": "PowerPoint"
        }

        return data