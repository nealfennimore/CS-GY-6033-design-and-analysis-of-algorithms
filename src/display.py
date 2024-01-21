from IPython.core.display import Image, Markdown
from IPython.display import display


class Display:
    @staticmethod
    def markdown(text: str):
        display(Markdown(text))

    @staticmethod
    def md(text: str):
        Display.markdown(text)

    @staticmethod
    def image(**kwargs):
        display(Image(**kwargs))
