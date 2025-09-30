from bs4 import BeautifulSoup


class SiteChecker:
    def __init__(self, page_content: str):
        self._parsed_page = BeautifulSoup(page_content, "html.parser")

    def check_for_h1(self) -> str:
        h1_tags = self._parsed_page.find_all("h1")
        for tag in h1_tags:
            if len(tag.contents) > 0:
                return tag.contents[0].text
        return ""

    def check_for_title(self) -> str:
        title = self._parsed_page.find("title")
        if title and len(title.contents) > 0:
            return title.contents[0].text
        return ""

    def check_for_meta_description(self) -> str:
        meta_tags = self._parsed_page.find_all("meta")
        for tag in meta_tags:
            if tag.attrs.get("name") == "description":
                if tag.attrs.get("content"):
                    return tag.attrs.get("content")
        return ""
