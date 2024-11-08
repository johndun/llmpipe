# LLMPipe Examples

## LlmPrompt Class Overview

The `LlmPrompt` class is the core component for creating structured LLM interactions. It provides a framework for defining inputs, outputs, and evaluations.

### Key Parameters

- `inputs`: List[Input] - Define the input fields expected by the prompt
- `outputs`: List[Output] - Define the output fields to be generated
- `task`: str - The main task description
- `details`: str - Additional task details or instructions
- `inputs_header`: str - Header text for the inputs section (default: "You are provided the following inputs:")
- `footer`: str - Optional footer text for the prompt
- `break_after_first_fail`: bool - Stop evaluation after first failure (default: True)

### Main Methods

- `__call__(**inputs)` - Generate outputs for given inputs
- `evaluate(**inputs)` - Run evaluations on outputs
- `revise(max_revisions=6, **inputs)` - Attempt to fix failing evaluations

### Automatic Features

- Generates structured prompts from inputs/outputs definitions
- Handles XML tag wrapping for outputs
- Validates outputs against requirements

This document provides examples of using the LLMPipe library for different use cases.

## Basic Usage

### Simple Question-Answer

The most basic usage is creating a prompt with a single input and output:

```python
from llmpipe import LlmPrompt, Input, Output

qa_prompt = LlmPrompt(
    inputs=[Input("question", "A question to answer")],
    outputs=[Output("answer", "A detailed answer to the question")],
    task="Provide a clear and accurate answer to the given question."
)

response = qa_prompt(question="What causes the seasons on Earth?")
print(response["answer"])
```

### Adding Chain-of-Thought

To improve reasoning, add a thinking step:

```python
math_solver = LlmPrompt(
    inputs=[Input("problem", "A mathematical word problem")],
    outputs=[
        Output("thinking", "Show your step-by-step reasoning"),
        Output("solution", "The final numerical answer")
    ],
    task="Solve the mathematical problem showing all your work.",
    details="Make sure to break down the problem into clear steps."
)

response = math_solver(problem="""
If a train travels at 60 mph for 2.5 hours, then increases 
speed to 75 mph for 1.5 hours, what is the total distance covered?
""")

print("Reasoning:", response["thinking"])
print("Answer:", response["solution"])
```

## Working with Evaluations

### Basic Input Validation

You can add evaluations to ensure outputs meet specific criteria:

```python
from llmpipe import LlmPrompt, Input, Output

password_generator = LlmPrompt(
    inputs=[Input("requirements", "Password requirements")],
    outputs=[
        Output(
            "password", 
            "A secure password",
            evaluations=[
                {"type": "max_chars", "value": 16},
                {"type": "no_blocked_terms", "value": ["password", "123", "admin"]},
                {"type": "no_square_brackets"}
            ]
        )
    ]
)

# Generate and validate
response = password_generator(requirements="Create a secure password")
eval_results = password_generator.evaluate(**response)
print("Password:", response["password"])
print("Evaluation:", eval_results)
```

### Auto-Revision with LLM Evaluations

Combine deterministic and LLM-based evaluations with auto-revision:

```python
from llmpipe import LlmPrompt, Input, Output, LlmEvaluation

story_generator = LlmPrompt(
    inputs=[Input("topic", "Story topic")],
    outputs=[
        Output(
            "story",
            "A short story",
            evaluations=[
                {"type": "max_chars", "value": 500},  # Deterministic
                LlmEvaluation(  # LLM-based
                    field="story",
                    requirement="Story must have a clear beginning, middle, and end",
                    use_cot=True
                )
            ]
        )
    ],
    task="Write an engaging short story on the given topic."
)

# Generate, evaluate, and auto-revise if needed
response = story_generator(topic="A day at the beach")
eval_results = story_generator.evaluate(**response)

if any(eval_results.values()):  # If any evaluations failed
    revised = story_generator.revise(topic="A day at the beach")
    print("Revised story:", revised["story"])
```

## Advanced Features

### Multiple Interdependent Outputs

Create prompts where outputs build on each other:

```python
analysis_prompt = LlmPrompt(
    inputs=[Input("text", "Text to analyze")],
    outputs=[
        Output("summary", "A brief summary"),
        Output(
            "sentiment",
            "Sentiment analysis",
            inputs=[Input("summary", "Text summary")]  # Uses previous output
        ),
        Output(
            "recommendations",
            "Action recommendations",
            inputs=[
                Input("summary", "Text summary"),
                Input("sentiment", "Sentiment analysis")
            ]
        )
    ]
)

response = analysis_prompt(text="Your text here...")
print("Summary:", response["summary"])
print("Sentiment:", response["sentiment"])
print("Recommendations:", response["recommendations"])
```

### Custom Evaluation Chains

Create complex evaluation chains with multiple steps:

```python
from llmpipe import LlmPrompt, Input, Output, LlmEvaluation

code_review = LlmPrompt(
    inputs=[Input("code", "Python code to review")],
    outputs=[
        Output(
            "review",
            "Code review comments",
            evaluations=[
                LlmEvaluation(
                    field="review",
                    requirement="Must address code style, performance, and security",
                    use_cot=True
                ),
                LlmEvaluation(
                    field="review",
                    requirement="Must provide specific examples for improvements",
                    use_cot=True
                )
            ]
        ),
        Output(
            "score",
            "Review score (1-10)",
            inputs=[Input("review", "Code review comments")],
            evaluations=[
                {"type": "is_in_allow_list", "value": list(map(str, range(1, 11)))}
            ]
        )
    ]
)

response = code_review(code="def example(): pass")
print("Review:", response["review"])
print("Score:", response["score"])
```

## Best Practices

1. Always include clear task descriptions
2. Use chain-of-thought for complex reasoning
3. Combine deterministic and LLM evaluations
4. Set appropriate evaluation criteria
5. Use the revision system for important outputs
6. Structure complex prompts with interdependent outputs

Remember that LLM responses can be non-deterministic, so always validate critical outputs.
