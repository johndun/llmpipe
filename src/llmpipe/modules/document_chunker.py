from typing import List, Dict

from llmpipe.field import Input, Output
from llmpipe.llmprompt import LlmPrompt
from llmpipe.llmprompt_formany import LlmPromptForMany


def _split_document_into_sections(document: str, breaks: list[str]) -> list[str]:
    """
    Split a document into sections based on a list of breaking points.
    Each section starts with one of the lines specified in breaks.

    Args:
        document: A string containing the full text document
        breaks: A list of strings, each being a complete line that should start a new section

    Returns:
        A list of strings, each containing a section of the document
    """
    # Convert document to list of lines and remove empty lines at start/end
    lines = document.splitlines()

    # Find indices where each break occurs
    break_indices = []
    for i, line in enumerate(lines):
        if line in breaks:
            break_indices.append(i)

    # If no breaks are found, return the entire document as one section
    if not break_indices:
        return [document]

    # Create sections using break points
    sections = []
    for i in range(len(break_indices)):
        start = break_indices[i]
        # If this is the last break, go to end of document
        if i == len(break_indices) - 1:
            end = len(lines)
        else:
            end = break_indices[i + 1]

        # Join lines for this section and add to results
        section = '\n'.join(lines[start:end])
        sections.append(section)

    return sections


class DocumentChunker:
    """Break a document into sections and subsections.

    - If the first subsection of the document contains only the title, it will have equal metadata keys: document == section == subsection
    - If a subsection contains only a section header, it will have equal metadata keys: section == subsection

    Initialization Parameters:
        **kwargs: Keyword arguments passed to `LlmPrompt`

    Args:
        document: The document to chunk
        document_title: An optional title for the document. One will be generated if not provided.

    Returns:
        A list of dictionaries with keys: document, section, subsection, content
    """
    def __init__(self, **kwargs):
        inputs = Input("document", "A document")
        chain_of_thought = Output("thinking", "Begin by thinking step by step")

        section_break = Output(
            name="break",
            description="A line indicating the beginning of a top-level section",
            inputs=[inputs],
            evaluations=[
                {
                    "type": "is_in_string_field",
                    "value": "document",
                    "label": "Must exactly match an entire line, including markdown formatting and any special characters, but not including newlines, from the document."
                }
            ]
        )
        self.chunker = LlmPromptForMany(
            task="Split the document (or document section) into top-level sections (or subsections)",
            details="Return the lines of the document or document section that break it into the top-level sections or subsections present. Each break line must exactly match an entire line, including markdown formatting and any special characters, but not including newlines, from the document. If a document- or section-level title is present, include it as the first section.",
            inputs=section_break.inputs,
            output=section_break,
            cot_string=chain_of_thought.description,
            **kwargs
        )

        header = Output(
            "header", "A section header",
            inputs=[{"name": "text", "description": "Text from a document"}]
        )
        self.titler = LlmPrompt(
            task="Generate a header, using title case and no formatting, for a document or a section of a document. If the text starts with a header, simply return it without markdown or other formatting.",
            inputs=header.inputs,
            outputs=[chain_of_thought, header],
            **kwargs
        )

    def _call(self, **inputs) -> List[Dict]:
        document = inputs["document"]
        results = self.chunker(**inputs)
        section_breaks = self.chunker.revise(**(inputs | results))["break"]
        if len(section_breaks) == 1:
            document_title = (
                inputs["document_title"] or
                self.titler(text=document)["header"]
            )
            return [{"title": document_title, "content": document}]

        sections = _split_document_into_sections(document, section_breaks)
        section_headers = [
            (
                self.titler(text=section)["header"]
                if len(section.strip().splitlines()) > 1 else
                inputs["document_title"]
            )
            for section in sections
        ]
        sections = [{"title": k, "content": v} for k, v in zip(section_headers, sections)]
        return sections

    def __call__(self, document: str, document_title: str = "") -> List[Dict]:
        if not document_title:
            print("Generating a document title...")
            document_title = self.titler(text=document)["header"]
        print("Performing top level segmentation...")
        sections = self._call(document=document, document_title=document_title)
        print(f"{len(sections)} sections identified")
        for idx, section in enumerate(sections):
            print(f"Performing segmentation of section {idx + 1}: {section['title']}...")
            subsections = self._call(document=section["content"], document_title=section["title"])
            print(f"{len(subsections)} subsections identified")
            section["content"] = subsections

        subsection_list = []
        for section in sections:
            section_title = section["title"]
            for subsection in section["content"]:
                subsection_title = subsection["title"]
                subsection_list.append({
                    "document": document_title,
                    "section": section_title,
                    "subsection": subsection_title,
                    "content": subsection["content"]
                })
        print(f"Chunked the document into {len(subsection_list)} sections.")
        return subsection_list
