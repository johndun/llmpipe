from typing import Dict, List

from llmpipe import LlmPrompt, Input, Output, LlmPromptForMany, LlmEvaluation
from datasets import Dataset


class ExemplarGenerator:
    """Returns a list of dictionaries containing passing/failing exemplars.

    - Inputs for the requirement are defined at class initialization
    - The evaluation is passed when the instance is called

    Initialization Parameters:
        input (Input): An `Input` for the evaluation.
        **kwargs: Keyword arguments passed to `LlmPrompt`

    Args:
        **inputs: Values for the inputs defined in `self.inputs`

    Returns:
        A list of dictionaries with additional keys: requirement, groundtruth
    """
    def __init__(self, input: Input, n: int = 5, **kwargs):
        self.n = n
        requirement = Input("requirement", f"A requirement for `{input.name}`")
        passing = Output(
            "example", "An example that meets the `requirement`", 
            inputs=[input, requirement],
            evaluations=[{
                "type": "llm", 
                "value": "Should not contain any comments about the requirement", 
                "use_cot": False
            }]
        )
        failing = Output(
            "example", "An example that does not meet the `requirement`", 
            inputs=passing.inputs, evaluations=passing.evaluations
        )
        cot = Output("thinking", "Begin by thinking step by step")
        self.pass_exemplar_generator = LlmPromptForMany(
            output=passing, 
            task=f"Generate {self.n} example code reviews that meet the requirement.", 
            **kwargs
        )
        self.fail_exemplar_generator = LlmPromptForMany(
            output=failing, 
            task=f"Generate {self.n} example code reviews that fail to meet the requirement.",
            **kwargs
        )

    def __call__(self, **inputs) -> List[Dict]:
        print("Generating passing exemplars...")
        passing_exemplars = self.pass_exemplar_generator(**inputs)
        print("Revising passing exemplars...")
        passing_exemplars = self.pass_exemplar_generator.revise(**(inputs | passing_exemplars))["example"]
        print("Generating failing exemplars...")
        failing_exemplars = self.fail_exemplar_generator(**inputs)
        print("Revising failing exemplars...")
        failing_exemplars = self.fail_exemplar_generator.revise(**(inputs | failing_exemplars))["example"]
        return [
            inputs | {"groundtruth": "PASS" if idx < len(passing_exemplars) else "FAIL", "review": x}
            for idx, x in enumerate(passing_exemplars + failing_exemplars)
        ]
