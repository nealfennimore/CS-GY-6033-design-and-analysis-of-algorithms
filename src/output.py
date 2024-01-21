from base64 import b64encode
from hashlib import sha1

from requests import get

from src.display import Display


class Output(str):
    def to_markdown(self):
        Display.markdown(
            f"""```mermaid
{self}
```"""
        )

    def to_url(self) -> str:
        img = b64encode(self.encode("utf8")).decode("ascii")
        return f"https://mermaid.ink/img/{img}"

    def to_blob_url(self, ext: str = "png") -> str:
        url = self.to_url()
        img_blob = get(url).content
        enc_img = b64encode(img_blob).decode("utf-8")
        return f"data:image/{ext};base64,{enc_img}"

    def to_image(self):
        Display.image(url=self.to_url())

    def to_markdown_image(self) -> str:
        url = self.to_url()
        alt = sha1(url.encode()).hexdigest()[:8]
        return f"![{alt}]({url})"

    def to_markdown_blob_image(self) -> str:
        url = self.to_blob_url()
        alt = sha1(url.encode()).hexdigest()[:8]
        return f"![{alt}]({url})"
