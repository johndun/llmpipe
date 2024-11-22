# Vignette: Structured Output Generation with LLMPipe

The purpose of this vignette is to provide a tutorial for constructing prompts for generating and evaluating structured outputs.

## Defining Inputs and Outputs

Let's start with the basics. We define prompts in terms of Inputs and Outputs. Inputs define what the user needs to provide to the prompt in order to get an output. Just a name and a description:

```python
from llmpipe import Input, Output, LlmPrompt

topic = Input("topic", "A topic for an essay")
```

An Output is like an Input, but with linked dependencies:

```python
essay = Output("essay", "An essay about a topic", inputs=[topic])
```

We have, at this point, enough to define a prompt:

```python
essay_writer = LlmPrompt(outputs=[essay], verbose=True)
print(essay_writer.prompt)
essay_writer(topic="Bias-variance tradeoff")
```

Adding chain of thought is as straightforward as adding another output:

```python
cot = Output("thinking", "Begin by thinking step by step")
essay_writer = LlmPrompt(outputs=[cot, essay], verbose=True)
print(essay_writer.prompt)
essay_writer(topic="Bias-variance tradeoff")
```

## Defining Evaluations

Outputs can have Evaluations associated with them. Define evaluations using dictionaries:

```python
essay = Output(
    "essay", "An essay about a topic", 
    inputs=[topic], 
    evaluations=[
        {"type": "llm", "value": "Has a title"},
        {"type": "llm", "value": "Uses markdown formatting for titles and headers"}
    ]
)
essay_writer = LlmPrompt(inputs=[topic], outputs=[cot, essay], verbose=True)
print(essay_writer.prompt)
sample = {"topic": "Bias-variance tradeoff"}
# Merge dictionaries using the "or" operator
response = sample | essay_writer(**sample)
response = sample | essay_writer.revise(**sample)
```

A nuance that needs to be kept in mind is that, by default, the inputs defined for an output are passed to the evaluation and revision prompts. Here are some of the evaluation types you can use:

1. `max_chars` - Limit maximum character length

```python
{"type": "max_chars", "value": 500}
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

```python
{
    "type": "llm",
    "value": "Must be a formal business tone",
    "use_cot": True,  # Enable chain-of-thought reasoning
    "inputs": ...,  # Override the default inputs for the evaluation
    ...  # Additional arguments passed to LiteLLM
}
```

## Prompt Examples

TODO