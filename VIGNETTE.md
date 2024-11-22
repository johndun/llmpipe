# Vignette: Structured Output Generation with LLMPipe

The purpose of this vignette is to provide a tutorial for constructing prompts for generating and evaluating structured outputs.

## Defining Inputs and Outputs

Let's start with the basics. We define prompts in terms of Inputs and Outputs. Inputs define what the user needs to provide to the prompt in order to get an output. Just a name and a description:

```python
from llmpipe import Input, Output, LlmPrompt

topic = Input("topic", "A topic for an essay")
```

At its simplest, an Output is just an Input:

```python
essay = Output("essay", "An essay about a topic")
```

We have, at this point, enough to define a prompt:

```python
essay_writer = LlmPrompt(inputs=[topic], outputs=[essay], verbose=True)
print(essay_writer.prompt)
essay_writer(topic="Bias-variance tradeoff")
```

Adding chain of thought is as straightforward as adding another output:

```python
cot = Output("thinking", "Begin by thinking step by step")
essay_writer = LlmPrompt(inputs=[topic], outputs=[cot, essay], verbose=True)
print(essay_writer.prompt)
essay_writer(topic="Bias-variance tradeoff")
```

## Defining Evaluations

Outputs can have Evaluations associated with them. Define evaluations using dictionaries:

```python
essay = Output(
    "essay", "An essay about a topic", 
    evaluations=[
        {"type": "llm", "value": "Has a title"},
        {"type": "llm", "value": "Uses markdown formatting for titles and headers"}, 
        {"type": "max_words", "value": 500}, 
    ]
)
essay_writer = LlmPrompt(inputs=[topic], outputs=[cot, essay], verbose=True)
print(essay_writer.prompt)
sample = {"topic": "Bias-variance tradeoff"}
# Merge dictionaries using the "or" operator
sample = sample | essay_writer(**sample)
sample = sample | essay_writer.revise(**sample)
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

## Initialize Prompts with Yaml

The easiest way to define a prompt is with yaml:

```python
import yaml
code_reviewer = LlmPrompt(**yaml.safe_load("""
verbose: True
inputs:
  - name: code
    description: Python code to review
outputs:
  - name: thinking
    description: Begin by thinking step by step
  - name: review
    description: Code review comments
    evaluations:
      - type: llm
        value: Addresses code style, performance, and security
      - type: llm
        value: Provides specific examples for improvements
  - name: score
    description: Review score (1-10)
    evaluations: 
      - type: is_in_allow_list
        value: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
"""))
print(code_reviewer.prompt)
sample = {"code": "def example(): pass"}
# Merge dictionaries using the "or" operator
sample = sample | code_reviewer(**sample)
sample = sample | code_reviewer.revise(**sample)
```

On the other hand, defining python objects can enable re using components across multiple prompts:

```python
topic = Input("topic", "An essay topic")
cot = Output("thinking", "Begin by thinking step by step")
essay = Output(
    "essay", "An essay about a topic", 
    evaluations=[
        {"type": "llm", "value": "Has a title"},
        {"type": "llm", "value": "Uses markdown formatting for titles and headers"}, 
        {"type": "max_words", "value": 500}, 
    ]
)
essay_with_comments = Output(
    "essay_with_comments", "An essay about a topic with inline comments", 
    evaluations=[
        {"type": "contains_xml", "value": ["comment"]}
    ]
)
revised_essay = Output(
    "revised_essay", "A revised essay that addresses all of the comments", 
    evaluations=[
        {"type": "not_contains", "value": ["<comment>",]},
        {"type": "llm", "value": "Has a title"},
        {"type": "llm", "value": "Uses markdown formatting for titles and headers"}, 
        {"type": "max_words", "value": 500}, 
    ]
)
writer = LlmPrompt(inputs=[topic], outputs=[cot, essay], verbose=True)
editor = LlmPrompt(inputs=[essay], outputs=[cot, essay_with_comments], verbose=True)
revisor = LlmPrompt(inputs=[essay_with_comments], outputs=[cot, revised_essay], verbose=True)

sample = {"topic": "Cellular Meiosis"}

sample = sample | writer(**sample)
sample = sample | writer.revise(**sample)

sample = sample | editor(**sample)
sample = sample | editor.revise(**sample)

sample = sample | revisor(**sample)
sample = sample | revisor.revise(**sample)

print(sample["revised_essay"])
```