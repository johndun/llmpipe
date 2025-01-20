from dataclasses import dataclass
import json
from itertools import chain

import polars as pl

from llmpipe.field import (
    Input, Output, TabularOutput, JsonlinesOutput, JsonOutput, output_factory
)
from llmpipe.prompt_module import PromptModule
from llmpipe.revisor_module import RevisorModule


# model = "claude-3-haiku-20240307"
model = "claude-3-5-sonnet-20241022"
verbose = True

topic = Output("topic", "A topic")
style = Output("style", "A poetry style")
n = Output("n", "The number of poems to write")

thinking = Output("scratchpad", "An area for notes and drafting your responses")
poem = Output(
    "poem", "A poem", 
    inputs=[topic, style], 
    evaluations=[
        {"type": "llm", "value": "Is a poem of the style"},
        {"type": "llm", "value": "Incorporates the topic"}
    ]
)
poem_table1 = TabularOutput(
    "poems", "A table of poems", 
    fields=[poem], 
    inputs=[n],
    evaluations=[{"type": "llm", "value": "Has `n` rows"}]
)
poem_table2 = TabularOutput(
    "poems", "A table of poems",
    fields=[topic, style, poem],
    inputs=[n],
    evaluations=[{"type": "llm", "value": "Has `n` rows"}]
)
poem_table3 = JsonlinesOutput(
    "poems", "A table of poems",
    fields=[topic, style, poem],
    inputs=[n],
    evaluations=[{"type": "llm", "value": "Has `n` rows"}]
)
p1 = PromptModule(
    inputs=[n, topic, style], 
    outputs=[thinking, poem_table1], 
    verbose=verbose,
    model=model
)
# print(p1.prompt)
# response = p1(n=5, topic="pirates", style="haiku")
# print(json.dumps(response, indent=2))

p2 = PromptModule(
    inputs=[n], 
    outputs=[poem_table3], 
    verbose=False,
    model=model
)
p3 = RevisorModule(
    outputs=[topic, style, poem], 
    verbose=False, 
    model=model
)
print(p2.prompt)

data = {"n": [4, 4]}

response = p2(**data, num_proc=2)
samples = list(chain(*response["poems"]))
data = pl.from_dicts(samples).to_dict(as_series=False)

data["style"] = ["haiku"] * len(data["style"])

data = p3(**data, num_proc=2)
data


# p3 = PromptModule(
#     inputs=[n], 
#     outputs=[thinking, poem_table3], 
#     verbose=True,
#     model=model, 
#     temperature=0.7, 
#     top_k=5000
# )
# print(p3.prompt)
# response = p3(n=[5, 6], num_proc=2)
# print(json.dumps(response, indent=2))
