# LLMPipe Usage

## Core Field Classes

The `field` module provides two key classes for defining inputs and outputs:

### Input Class

The `Input` class defines fields that will be provided to prompts:

```python
from llmpipe import Input

question = Input(
    name="question",
    description="The question to be answered"
)
```

Key features:
- Generates XML tags for structured input
- Provides markdown formatting
- Creates input templates with placeholders

### Output Class

The `Output` class extends `Input` to add evaluation capabilities:

```python
from llmpipe import Output

answer = Output(
    name="answer",
    description="A detailed answer to the question",
    evaluations=[
        {"type": "max_chars", "value": 500},
        {"type": "no_blocked_terms", "value": ["idk", "unknown"]}
    ],
    inputs=[question]  # Define inputs needed to generate this output
)
```

Key features:
- Supports multiple evaluation types
- Can reference input fields needed for generation
- Automatically converts evaluation configs into evaluation objects

## Evaluation Classes

The `evaluations` module provides a framework for validating LLM outputs through various evaluation types:

### Core Evaluation Types

- `MaxCharacters`: Ensures output length is within limits
- `NoBlockedTerms`: Checks for absence of specified terms
- `NotInBlockedList`: Checks if an output is in a blocked list
- `IsInAllowList`: Validates output against allowed values
- `NoSlashes`, `NoSquareBrackets`: Enforce formatting rules
- `LlmEvaluation`: Uses LLM to evaluate complex criteria

### Using Evaluations

Evaluations can be added to Output fields as dictionaries:

```python
from llmpipe import Output, LlmEvaluation

# 1. Using dictionary configuration
output = Output(
    name="summary",
    description="A concise summary",
    evaluations=[
        {"type": "max_chars", "value": 200},
        {"type": "no_blocked_terms", "value": ["skip", "unknown"]}
    ]
)
```

#### Available Evaluation Configurations

The following evaluation types can be configured through dictionaries passed to Output's `evaluations` parameter:

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
# Dynamic list from input field
{"type": "not_in_blocked_list_field", "value": "forbidden_values"}
```

4. `is_in_allow_list` - Validate against allowed values

```python
{"type": "is_in_allow_list", "value": ["option1", "option2"]}
# Dynamic list from input field
{"type": "is_in_allow_list_field", "value": "allowed_values"}
```

5. `no_slashes` - Prevent slash-based placeholders

```python
{"type": "no_slashes"}
```

6. `no_square_brackets` - Prevent bracket-based placeholders

```python
{"type": "no_square_brackets"}
```

7. `no_long_words` - Limit word length

```python
{"type": "no_long_words", "value": 15}
```

8. `llm` - LLM-based evaluation

```python
{
    "type": "llm",
    "value": "Must be a formal business tone",
    "use_cot": True,  # Enable chain-of-thought reasoning
    ...  # Additional arguments passed to LiteLLM
}
```

### Evaluation Results

Each evaluation returns an `EvalResult` containing:

- `evaluation_result`: 'PASS' or 'FAIL'
- `reason`: Explanation of the result. Blank when evaluation result is 'PASS'.

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

# Print the generated prompt template
print(qa_prompt.prompt)

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
import logging
logging.basicConfig(level=logging.INFO)

from llmpipe import LlmPrompt, Input, Output, LlmEvaluation


story_generator = LlmPrompt(
    inputs=[Input("topic", "Story topic")],
    outputs=[
        Output(
            "story",
            "A short story",
            evaluations=[
                {"type": "max_chars", "value": 500},  # Deterministic
                {
                    "type": "llm", 
                    "value": "Story must have a clear beginning, middle, and end",
                    "use_cot": True
                }
            ]
        )
    ],
    task="Write an engaging short story on the given topic."
)

# Generate, evaluate, and auto-revise if needed
response = story_generator(topic="A day at the beach")
revised = story_generator.revise(**response)
print("Revised story:", revised["story"])
```

## Advanced Features

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
                {
                    "type": "llm", 
                    "value": "Must address code style, performance, and security",
                    "use_cot": True
                },
                {
                    "type": "llm", 
                    "value": "Must provide specific examples for improvements",
                    "use_cot": True
                }
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
eval_result = code_review.evaluate(code="def example(): pass", **response)
print("Review:", response["review"])
print("Score:", response["score"])
print("Evaluation Result:", eval_result)

```
