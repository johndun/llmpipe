from llmpipe.modules import DocumentChunker
from llmpipe import LlmPrompt, LlmPromptForMany, Input, Output


with open("experiments/tutorial/diataxis_tutorials_guidelines.txt", "r") as fin:
    guide = fin.read()


chunker = DocumentChunker()
print(chunker.chunker.prompt)

sections = chunker(document=guide)

outline = ""
for section in sections:
    if section["document"] == section["section"] == section["subsection"]:
        outline += section["document"] + "\n"
    elif section["section"] == section["subsection"]:
        outline += "- " + section["section"] + "\n"
    else:
        outline += "  - " + section["subsection"] + "\n"
print(outline)

with open("experiments/tutorial/")