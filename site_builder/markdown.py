import pydantic
import pandoc
import datetime
from bs4 import BeautifulSoup
from typing import Any
import yaml
import dateparser


class MarkdownMetadata(pydantic.BaseModel):
    title: str
    date: datetime.date
    tags: list[str] = pydantic.Field(default_factory=list)
    draft: bool = False


class Markdown:
    metadata_marker = "---"

    def __init__(self, filename: str, contents: str) -> None:
        self.filename = filename
        self.contents = contents
        self.md_body = self._parse_body(self.contents)
        self.html_body = self._process_html_body(self._md_to_html(self.md_body))
        self.html_preview = self.html_body.replace("'", '"').replace("\n", "")
        self.metadata = self._parse_metadata(contents)

    def _process_html_body(self, html_body: str) -> str:
        return html_body.replace('src="assets', 'src="/assets/site_assets')

    def _parse_body(self, contents: str) -> str:
        if not contents.startswith(self.metadata_marker):
            return contents

        end_idx = contents.find(self.metadata_marker, len(self.metadata_marker))
        if end_idx < 0:
            raise ValueError("Unable to find end of metadata section")

        body = self.contents[end_idx + len(self.metadata_marker) :]
        return body

    def _md_to_html(self, md_body: str) -> str:
        doc = pandoc.read(md_body)
        return pandoc.write(doc, format="html")

    def _parse_metadata(self, contents: str) -> MarkdownMetadata:
        if not contents.startswith(self.metadata_marker):
            return MarkdownMetadata(**{})

        start_idx = len(self.metadata_marker)
        end_idx = contents.find(self.metadata_marker, len(self.metadata_marker))

        if end_idx < 0:
            raise ValueError("Unable to find end of metadata section")

        metadata_section = self.contents[start_idx:end_idx]
        metadata = yaml.safe_load(metadata_section)

        # Post-process metadata
        # Clean up date and set to now if doesn't exist
        date_str: str = metadata.get("date", datetime.datetime.now().date().isoformat())
        date = dateparser.parse(str(date_str))
        if not date:
            raise ValueError("Invalid date")
        metadata["date"] = date
        metadata["tags"] = metadata.get("tags", [])

        return MarkdownMetadata(**metadata)

    def _parse_title(self, html_body: str) -> str:
        # If the title isn't provided in the medata, find it in the
        # html by searching for the first h1 tag
        soup = BeautifulSoup(html_body, "html.parser")
        title_tag = soup.find("h1")
        if not title_tag:
            raise ValueError("Unable to find title")
        return title_tag.text

    def as_record(self) -> dict[str, Any]:
        return {
            "title": self.metadata.title,
            "date": self.metadata.date.isoformat(),
            "pretty_date": self.metadata.date.strftime("%Y-%m-%d"),
            "raw_contents": self.contents,
            "body": self.md_body,
            "html_body": self.html_body,
            "html_preview": self.html_preview,
            "metadata": self.metadata.dict(),
        }
