import re
from dataclasses import dataclass
from typing import List


@dataclass
class XmlBlock:
    tag: str
    content: str

    def __repr__(self):
        return f"<{self.tag}>{self.content}</{self.tag}>"


def parse_text_for_tags(text: str) -> List[XmlBlock]:
    """Extracts the text within all the outermost XML/HTML tags.

    Args:
        text (str): A string with XML tags

    Returns:
        List[XmlBlock]: A list of XmlBlock objects, each containing the tag name and the content inside the tag block
    """
    if not text:
        return []
    pattern = r'<([^<>]+)>((?:(?!</?\1>)[\s\S])*)</\1>'
    matches = re.finditer(pattern, text, re.DOTALL)
    return [XmlBlock(match.group(1), match.group(2)) for match in matches]


def parse_text_for_tag(text: str, tag: str) -> List[str]:
    """Extracts the text within all the outermost specified XML/HTML tag.

    Args:
        text (str): A string with XML tags
        tag (str): The tag, without angle braces, to extract

    Returns:
        List[str]: A list of strings, each representing the content inside a tag block
    """
    return [x.content for x in parse_text_for_tags(text) if x.tag == tag]


def parse_text_for_one_tag(text: str, tag: str) -> str:
    """Extracts the (last) text contained in the specified XML/HTML tag.

    Args:
        text (str): A string with XML tags
        tag (str): The tag, without angle braces, to extract

    Returns:
        List[str]: A list of strings, each representing the content inside a tag block
    """
    results = parse_text_for_tag(text, tag)
    return results[-1] if results else ""