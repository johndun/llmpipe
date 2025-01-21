# Vignette: Structured Output Generation with LLMPipe

Use `llmpipe` to define and execute prompts to generate structured outputs.

## Defining Inputs and Outputs

Define prompts in terms of Inputs and Outputs. Inputs define what needs to be provided to the prompt in order to get an output. Just a name and a description:

```python
from llmpipe import Input, Output, PromptModule, RevisorModule

topic = Input("topic", "A topic for an essay")
```

At its simplest, an Output is just an Input:

```python
essay = Output("essay", "An essay about a topic")
```

There are few output class variants:

```python
from llmpipe import JsonlinesOutput, TabularOutput, JsonOutput
```

- `JsonOutput`: Outputs are passed through `json.loads(...)`
- `JsonLinesOutput`: Outputs are loaded as a jsonlines text file and returned as a list of dictionaries
- `TabularOutput`: Outputs are loaded as a tab-separated-values text file and returned as a list of dictionaries

Defining a prompt:

```python
essay_writer = PromptModule(inputs=[topic], outputs=[essay], verbose=True)
essay_writer(topic="Bias-variance tradeoff")
```

Adding chain of thought is as straightforward as adding another output:

```python
cot = Output("thinking", "Begin by writing an outline")
essay_writer = PromptModule(inputs=[topic], outputs=[cot, essay], verbose=True)
print(essay_writer.prompt)
essay_writer(topic="Bias-variance tradeoff")
```

## Defining Evaluations

Outputs can have Evaluations associated with them. Define evaluations using dictionaries:

```python
from llmpipe import Input, Output, PromptModule, RevisorModule

topic = Input("topic", "A topic for an essay")
cot = Output("thinking", "Begin by writing an outline")
essay = Output(
    "essay", "An essay about a topic",
    evaluations=[
        {"type": "llm", "value": "Has a title"},
        {"type": "llm", "value": "Uses markdown formatting for titles and headers"},
        {"type": "max_words", "value": 500},
    ]
)
writer = PromptModule(inputs=[topic], outputs=[cot, essay], verbose=True)
editor = RevisorModule(inputs=[topic], outputs=[cot, essay], verbose=True)
print(writer.prompt)
sample = {"topic": "Bias-variance tradeoff"}
sample = sample | writer(**sample)
print(editor.outputs[-1].evaluations[0].generator.prompt)
sample = sample | editor.revise(**sample)
```

Here are some of the evaluation types you can use:

1. `max_chars` - Limit maximum character length

```python
{"type": "max_chars", "value": 500}
```

2. `max_words` - Limit maximum number of words

```python
{"type": "max_words", "value": 100}
```

2. `no_blocked_terms` - Prevent specific terms in an output

```python
{"type": "no_blocked_terms", "value": ["skip", "unknown", "idk"]}
# Dynamic list from input field
{"type": "not_in_blocked_list_field", "value": "additional_blocked_terms"}
```

3. `not_in_blocked_list` - Check that an output isn't identical to any of a blocked list of values

```python
# Static list
{"type": "not_in_blocked_list", "value": ["bad1", "bad2"]}
# You can also define the blocked list in a field, e.g., `forbidden_values`.
{"type": "not_in_blocked_list_field", "value": "forbidden_values"}
```

4. `is_in_allow_list` - Validate against allowed values

```python
{"type": "is_in_allow_list", "value": ["option1", "option2"]}
# Dynamic list from input field
{"type": "is_in_allow_list_field", "value": "allowed_values"}
```

5. `llm` - LLM-based evaluation

A nuance that needs to be kept in mind for LLM-based evaluations is that the inputs may need to be carefully defined. By default, evaluation inputs are inherited from the Output or LlmPrompt when initialized. But they can be overridden. For example, if you have one or more large inputs, say a long document, but are evaluating the response for something that does not require the original document, you can save a lot of tokens by explicitly defining the evaluation inputs.

```python
{
    "type": "llm",
    "value": "Must be a formal business tone",
    "use_cot": True,  # Enable chain-of-thought reasoning
    "inputs": ...,  # Override the default inputs for the evaluation.
    ...  # Additional arguments passed to LiteLLM
}
```

## Tabular Outputs

`JsonlinesOutput` and `TabularOutput` output types can be used to generate small tables of outputs (with predefined fields).

Only really tested up to around 20 rows. Seems to work well with <10 rows.

```python
import json
from itertools import chain

import polars as pl

from llmpipe import Input, Output, JsonlinesOutput, PromptModule, RevisorModule


# Config
model = "claude-3-5-sonnet-20241022"
verbose = True

# Inputs
n = Output("n", "The number of poems to write")

# Outputs
thinking = Output("scratchpad", "An area for notes and drafting your responses")
topic = Output("topic", "A topic")
style = Output("style", "A poetry style")
poem = Output(
    "poem", "A poem",
    inputs=[topic, style],
    evaluations=[
        {"type": "llm", "value": "Is a poem of the style"},
        {"type": "llm", "value": "Incorporates the topic"}
    ]
)
poem_table = JsonlinesOutput(
    "poems", "A table of poems",
    fields=[topic, style, poem],
    inputs=[n],
    evaluations=[{"type": "llm", "value": "Has `n` rows"}]
)

poet = PromptModule(
    inputs=[n],
    outputs=[thinking, poem_table3],
    verbose=False,
    model=model
)
# print(poet.prompt)
# response = poet(n=5)
# print(json.dumps(response, indent=2))
critic = RevisorModule(
    outputs=[topic, style, poem],
    verbose=False,
    model=model
)

data = {"n": [4, 4]}
response = poet(**data, num_proc=2)
# Flatten the lists of poems
samples = list(chain(*response["poems"]))
data = pl.from_dicts(samples).to_dict(as_series=False)
data = critic(**data, num_proc=2)
data
```

END