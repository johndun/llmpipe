from dataclasses import dataclass
from typing import List

from llmpipe import Input, Output, PromptModule


@dataclass
class DocumentChunker(PromptModule):
    """A module for chunking documents into semantically meaningful segments."""

    def __post_init__(self):
        self.document = Input("document", "A document")
        
        self.task = """\
Given a document containing text and/or code, identify meaningful semantic chunk boundaries that preserve context and readability.

Generate individual, complete lines from the document that start semantically meaningful chunks.

Rules for text:
- Begin new chunks at transitions in topic, argument, or narrative
- Start chunks at structural elements (sections, paragraphs)
- Keep chunks concise, but with enough context to be interpretable in isolation"""

        self.cot = """\
Analyze step by step:
1. Identify natural content/code breaks
2. Evaluate semantic independence of chunks
3. Verify context preservation
4. Confirm exact document line matches"""

        self.breaks_format = """\
Lines from document that begin semantically meaningful chunks.
Each line must exactly match a complete line from document."""

        super().__post_init__()
        
        self.inputs = [self.document]
        self.outputs = [
            Output("thinking", self.cot),
            Output("breaks", self.breaks_format)
        ]

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
        breaks = [x.strip() for x in response["breaks"].split("\n") if x.strip()]
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
