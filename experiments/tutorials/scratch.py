import json
from llmpipe.modules import DocumentChunker, ConvertListToJson
from llmpipe import LlmPrompt, LlmPromptForMany, Input, Output, LlmEvaluation


with open("experiments/tutorials/diataxis_tutorials_guidelines.txt", "r") as fin:
    document = fin.read()

# chunker = DocumentChunker()
# sections = chunker(document=guide)

# with open("experiments/tutorials/guidelines_chunked.jsonl", "w") as fout:
#     fout.write("\n".join([json.dumps(section) for section in sections]))

# outline = ""
# for section in sections:
#     if section["document"] == section["section"] == section["subsection"]:
#         outline += section["document"] + "\n"
#     elif section["section"] == section["subsection"]:
#         outline += "- " + section["section"] + "\n"
#     else:
#         outline += "  - " + section["subsection"] + "\n"
# print(outline)



guide = Input("guide", "A guide for writing tutorials")
cot = Output("thinking", "Begin by thinking step by step")
topic = Input("topic", "A topic for a data science or coding tutorial")
list_converter = ConvertListToJson()




# Outline Rubrik
outline_rubrik_output = Output(
    "rubrik", "An evaluation rubrik for an outline of a tutorial on a data science or coding topic",
    evaluations=[
        {
            "type": "llm",
            "value": "Includes no unrealistic requirements, for example, that *all* sections include some kind of content (many documents have introduction and closing sections with very different content)",
        },
        {
            "type": "llm",
            "value": "Evaluates an outline of a tutorial, not the tutorial itself",
        },
        {
            "type": "llm",
            "value": "Does not include requirements related to external references, links, or citations",
        },
        {
            "type": "llm",
            "value": "Does not include requirements related to prerequisites or scope or time to complete",
        },
    ]
)
outline_rubrik_task = "Using the provided guide, create a rubrik for evaluating outlines for data science and coding tutorials targeting a scientist/engineer audience."
outline_rubrik_details = """\
The rubrik should provide a checklist for evaluating outlines of tutorials on technical topics. The rubrik should be a  flat list consisting of requirements and success criteria. Each evaluation should start with an imperative sentence beginning with a verb or verb phrase (e.g., contains, addresses, has, provides, etc.). After, provide additional detail and examples as needed to help a grader perform the evaluation."""

outline_rubrik_prompt = LlmPrompt(
    task=outline_rubrik_task,
    details=outline_rubrik_details,
    inputs=[guide],
    outputs=[cot, outline_rubrik_output]
)
response = outline_rubrik_prompt(guide=document)
revised_response = outline_rubrik_prompt.revise(guide=document, **response)
outline_rubrik_str = revised_response["rubrik"]
print(outline_rubrik_str)

outline_rubrik = list_converter(outline_rubrik_str)
print(*outline_rubrik, sep="\n---\n")

with open("experiments/tutorials/outline_rubrik.json", "w") as fout:
    json.dump(outline_rubrik, fout)

with open("experiments/tutorials/outline_rubrik.json", "r") as fin:
    outline_rubrik = json.load(fin)


outline_evals = [{"type": "llm", "value": x} for x in outline_rubrik]
outline_evals.append({"type": "llm", "value": "Does not include time to complete"})
outline_evals.append({"type": "llm", "value": "Contains sections and subsections"})
outline_output = Output(
    "outline", "An outline, containing header titles and 1-sentence descriptions of sections and subsections, for a data science or coding tutorial",
    evaluations=outline_evals
)
outline_generator = LlmPrompt(
    task="Write an outline for a tutorial on the provided topic",
    inputs=[topic],
    outputs=[cot, outline_output]
)

inputs = {"topic": "K-means clustering"}
outline_response = outline_generator(**inputs)
outline_response = outline_generator.revise(**inputs, **outline_response)
outline_str = outline_response["outline"]
print(outline_str)

with open("experiments/tutorials/outline.txt", "w") as fout:
    fout.write(outline_str)

generate_headers = LlmPrompt(
    task="Convert the outline to a json list of markdown-formatted section and subsection headers.",
    details="""Use "##" for section headers and "###" for subsections. Include the title if present. Output should be a json list: ["item1", "item2", ...]. Do not include descriptions if they are present, just the headers for the sections and subsections.""",
    inputs=[Input("outline", "An outline for a document")],
    outputs=[
        Output("outline_list", "A json list containing markdown-formatted section headers")
    ]
)
outline_list = generate_headers(outline=outline_str)["outline_list"]
outline = json.loads(outline_list)
print(*outline, sep="\n")

with open("experiments/tutorials/outline.json", "w") as fout:
    json.dump(outline, fout)

with open("experiments/tutorials/outline.txt", "r") as fin:
    outline_str = fin.read()
with open("experiments/tutorials/outline.json", "r") as fin:
    outline = json.load(fin)


summarize_prompt = LlmPrompt(
    task="Write a concise, single-paragraph summary of the guidelines",
    inputs=[guide],
    outputs=[
        cot,
        Output("guidelines", "Concise (single-paragraph) guidelines for tutorial writing")
    ]
)
guidelines = summarize_prompt(guide=document)["guidelines"]
print(guidelines)



# Single Section Rubrik
section_rubrik_output = Output(
    "rubrik", "An evaluation rubrik for a single section of a tutorial on a data science or coding topic",
    evaluations=[
        {
            "type": "llm",
            "value": "Includes no unrealistic requirements, for example, asserting that all explanations be a single sentence (there will obviously be topics where this is infeasible).",
        },
        {
            "type": "llm",
            "value": "Does not include requirements related to external references, links, or citations",
            "use_cot": False
        },
        {
            "type": "llm",
            "value": "Does not include requirements related to time to complete",
            "use_cot": False
        },
        {
            "type": "llm",
            "value": "Does not include requirements related to images",
            "use_cot": False
        }
    ]
)
section_rubrik_task = "Using the provided guide, create an evaluation rubrik for individual section text for data science and coding tutorials"
section_rubrik_details = """\
The rubrik should provide a checklist that enables identification of high quality tutorial text. The rubrik should be a  flat list consisting of requirements and success criteria. Each rubrik item should start with an imperative sentence beginning with a verb or verb phrase (e.g., contains, addresses, has, provides, etc.). After, provide additional detail and examples as needed to help a grader perform the evaluation."""

section_rubrik_prompt = LlmPrompt(
    task=section_rubrik_task,
    details=section_rubrik_details,
    inputs=[guide],
    outputs=[cot, section_rubrik_output]
)

response = section_rubrik_prompt(guide=document)
revised_response = section_rubrik_prompt.revise(guide=document, **response)
section_rubrik_str = revised_response["rubrik"]
section_rubrik = list_converter(section_rubrik_str)
print(*section_rubrik, sep="\n---\n")

with open("experiments/tutorials/section_rubrik.json", "w") as fout:
    json.dump(section_rubrik, fout)


with open("experiments/tutorials/section_rubrik.json", "r") as fin:
    section_rubrik = json.load(fin)


section_evals = [{"type": "llm", "value": x} for x in section_rubrik]
section_evals.append({"type": "llm", "use_cot": False, "value": """Does not contain and section ("##") or subsection ("###") headers"""})
section_text_output = Output(
    "section_text", "Text for the next section",
    evaluations=section_evals
)
generate_section = LlmPrompt(
    task="""Generate text for the next section of a data science or coding tutorial. The section or subsection to be written is indicated by the header at the end of `wip`. Additional details about the section (or subsection) can be found in the `outline`.""",
    details="Tutorial Writing Guidelines:\n\n" + guidelines,
    inputs=[
        topic,
        Input("outline", "Outline of the tutorial"),
        Input("wip", "Previously drafted sections, ending with a header of the next section or subsection to be written"),
    ],
    outputs=[cot, section_text_output]
)
print(generate_section.prompt)

document = []
for idx, section_header in enumerate(outline):
    document.append(section_header)
    if len(document) < 5:
        subdoc = document
    else:
        subdoc = [document[0], "..."] + document[-4:]
    inputs = {"topic": "K-means clustering", "wip": "\n\n".join(subdoc), "outline": outline_str}
    print(section_header)
    section_response = generate_section(**inputs)
    print(section_response["section_text"])
    print(generate_section.tokens.total)
    # if section_header.startswith("###") or idx > 1:
    #     section_response = generate_section.revise(**(inputs | section_response))
    document.append(section_response["section_text"])

print(document)
with open("experiments/tutorials/out.txt", "w") as fout:
    fout.write("\n\n".join(document))

with open("experiments/tutorials/out.json", "w") as fout:
    json.dump(document, fout)


