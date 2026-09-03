from pptx import Presentation
from pptx.util import Inches


class PPTService:

    def create(self):

        prs = Presentation()

        prs.slide_width = Inches(13.33)

        prs.slide_height = Inches(7.5)

        return prs