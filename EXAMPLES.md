# Examples

Define LLM prompt functions in terms of inputs and outputs:

```python
from llmpipe import LlmPrompt, Input, Output, LlmEvaluation


haiku_generator = LlmPrompt(
    inputs=[Input("topic", "A topic for a haiku")],
    outputs=[Output("haiku", "A haiku")]
)
response = haiku_generator(topic="clouds")

print(haiku_generator.history[0]["content"])
print(response["haiku"])
```

Adding chain-of-thought can be done by adding additional outputs:

```python
answer_generator = LlmPrompt(
    inputs=[Input("problem", "A math problem")],
    outputs=[
        Output("thinking", "Begin by thinking step-by-step"),
        Output("answer", "Answer to the problem")
    ]
)

response = answer_generator(problem="""
A store has a 20% off sale, then takes an additional 15% off at checkout.
If you buy a $100 item, what's the final price?
""")

print(answer_generator.history[0]["content"])
print(response["thinking"])
print(response["answer"])
```

Llm-as-a-judge evaluations:

```python
check_answer = LlmEvaluation(
    field="answer",
    field_description="Answer to the question",
    inputs=[Input("question", "A question")],
    requirement="Correctly answers the question",
    use_cot=True
)
response = check_answer(question="What is the capital of France?", answer="London")
for turn in check_answer.generator.history:
    print(turn["content"])
print(response)
```

Define requirements for outputs. This enables evaluating and revising outputs:

```python
from llmpipe import LlmPrompt, Input, Output, LlmEvaluation
primary_color = Output(
    name="color", description="A color",
    inputs=[Input("object", "An object to color")],
    evaluations=[{"type": "is_in", "value": ["red", "blue", "yellow"]}]
)
non_primary_color = Output(
    name="color", description="A color",
    inputs=[Input("object", "An object to color")],
    evaluations=[{"type": "not_in_blocked_list", "value": ["red", "blue", "yellow"]}]
)
color_picker1 = LlmPrompt(inputs=primary_color.inputs, outputs=[primary_color])
color_picker2 = LlmPrompt(inputs=non_primary_color.inputs, outputs=[non_primary_color])

inputs = {"object": "A submarine"}
response = color_picker1(**inputs)
first_eval = color_picker2.evaluate(**response)
revised = color_picker2.revise(**response, max_revisions=1)
second_eval = color_picker2.evaluate(**revised)
print(response, first_eval, revised, second_eval, sep="\n")
```
