from pptx.util import Inches

from ppt.components import PPTComponents
from models.theme import Theme


class DashboardSlide:

    @staticmethod
    def create(prs, presentation):

        slide = prs.slides.add_slide(prs.slide_layouts[6])

        PPTComponents.draw_header(
            slide,
            "Executive Dashboard"
        )

        cards = [

            ("Articles", presentation.total_articles),

            ("Sources", presentation.total_sources),

            ("Innovation",
             f"{presentation.avg_innovation_score:.1f}"),

            ("Enterprise",
             presentation.enterprise_ready)

        ]
        x = 0.5

        for title, value in cards:

            PPTComponents.draw_card(

                slide,

                x,

                0.9,

                2.8,

                1.1,

                title,

                value

            )

            x += 3.1

            risk_text = (

            f"🟢 Low : {presentation.low_risk}\n"

            f"🟡 Medium : {presentation.medium_risk}\n"

            f"🔴 High : {presentation.high_risk}"

        )

        PPTComponents.draw_section(

            slide,

            0.6,

            2.5,

            5.8,

            2.2,

            "Risk Distribution",

            risk_text

        )

        technologies = "\n".join(

            presentation.top_technologies[:8]

        )

        PPTComponents.draw_section(

            slide,

            6.8,

            2.5,

            5.8,

            2.2,

            "Top Technologies",

            technologies

        )

        PPTComponents.draw_footer(

            slide,

            "AI-PPT-Agent Executive Dashboard"

        )