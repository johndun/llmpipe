# Vignette: Structured Output Generation with LLMPipe

The purpose of this vignette is to provide a tutorial for constructing prompts for generating and evaluating structured outputs.

## Defining Inputs and Outputs

Let's start with the basics. We define prompts in terms of Inputs and Outputs. Inputs define what the user needs to provide to the prompt in order to get an output. Just a name and a description:

```python
from llmpipe import Input, Output, PromptModule, RevisorModule

topic = Input("topic", "A topic for an essay")
```

At its simplest, an Output is just an Input:

```python
essay = Output("essay", "An essay about a topic")
```

We have, at this point, enough to define a prompt:

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
# Merge dictionaries using the "or" operator
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