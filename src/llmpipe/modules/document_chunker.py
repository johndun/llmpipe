from dataclasses import dataclass
from typing import List

from llmpipe import Input, Output, PromptModule


@dataclass
class DocumentChunker(PromptModule):
    """A module for chunking documents into semantically meaningful segments."""

    def __post_init__(self):
        self.document = Input("document", "A document")
        
        self.task = """\
Given a document containing text and/or code, identify logical top-level section boundaries.

Generate individual, complete lines from <document> that break the document into logical sections.

Rules for break lines:

- Break lines should be the first line of each section.
- Start sections at key structural elements: sections, paragraphs, functions, etc.
- Each line must be a complete line (e.g., all text between two newlines) from the document, including whitespace, indentation, markdown formatting, and special characters.
  - Be especially careful to use the right number of hash marks for markdown headers.
  - Break lines must be complete lines, even when a line includes mismatched XML tags.
- If a document cannot be broken into smaller sections, output the first line as the only break.

The document begins here:"""

        self.breaks_format = """\
Lines from <document> that break the document into logical sections."""

        self.inputs = [self.document]
        self.outputs = [Output("breaks", self.breaks_format)]

        super().__post_init__()

    def chunk_text(self, text: str, breaks: List[str]) -> List[str]:
        """
        Chunks text into segments based on break lines.

        Args:
            text: Document text to be chunked
            breaks: List of strings that should be treated as first lines of chunks

        Returns:
            List of text chunks that concatenate to the original text
        """
        # Split text into lines while preserving line endings
        lines = text.splitlines(keepends=True)
        if not lines:
            return []

        # Find indices where breaks occur
        break_indices = []
        text_lines_set = {line.rstrip() for line in lines}  # Remove trailing whitespace for comparison

        for break_line in breaks:
            if break_line.rstrip() not in text_lines_set:
                print(f"Warning: Break line '{break_line}' not found in text")
                continue

            # Find all occurrences of the break line
            for i, line in enumerate(lines):
                if line.rstrip() == break_line.rstrip():
                    break_indices.append(i)

        break_indices.sort()

        # Handle case where no valid breaks were found
        if not break_indices:
            return [text]

        # Create chunks using break indices
        chunks = []
        for i in range(len(break_indices)):
            start = break_indices[i]
            end = break_indices[i + 1] if i + 1 < len(break_indices) else len(lines)
            chunk = ''.join(lines[start:end])
            chunks.append(chunk)

        # Add text before first break if it exists
        if break_indices[0] > 0:
            first_chunk = ''.join(lines[:break_indices[0]])
            chunks.insert(0, first_chunk)

        return chunks

    def __call__(self, document: str) -> List[str]:
        """
        Chunk a document into semantically meaningful segments.

        Args:
            document: The text document to chunk

        Returns:
            List of text chunks
        """
        response = super().__call__(document=document)
        breaks = [x for x in response["breaks"].split("\n") if x.strip()]
        return self.chunk_text(document, breaks)


# Example usage:
if __name__ == "__main__":
    chunker = DocumentChunker(
        model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
        verbose=True
    )
    
    sample_text = "Your document text here..."
    chunks = chunker(sample_text)
    
    for chunk in chunks:
        print(80 * "-")
        print(chunk)
