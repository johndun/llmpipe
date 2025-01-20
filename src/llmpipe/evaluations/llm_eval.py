from dataclasses import dataclass, field
from typing import List

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class LlmEvaluation(Evaluation):
    """An LLM-as-a-judge evaluation"""
    type: str = "llm"
    use_cot: bool = False  #: If true, add a chain-of-thought request
    inputs: List[Input] = field(default_factory=lambda: [])  #: Inputs needed to perform the evaluation
    field_description: str = ""  #: Description of the field to apply the evaluation to

    @property
    def tokens(self):
        return self.generator.tokens

    def __post_init__(self, **kwargs):
        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

        chain_of_thought = Output("thinking", "Begin by thinking step by step")
        evaluation_result = Output(
            name="evaluation_result",
            description=f'PASS if `{self.field}` meets the requirement described in `requirement`, FAIL otherwise',
            inputs=(
                self.inputs +
                [Input(self.field, self.field_description)] +
                [Input("requirement", f"A requirement for `{self.field}`")]
            ),
            evaluations=[{"type": "is_in", "value": ["PASS", "FAIL"]}]
        )
        reason = Output("reason", "A reason for the evaluation result. Leave blank when the evaluation passes.")

        self.generator = PromptModule(
            task="Determine if an input meets a requirement.",
            inputs=evaluation_result.inputs,
            outputs=(
                [chain_of_thought, evaluation_result, reason]
                if self.use_cot else
                [evaluation_result, reason]
            ),
            **kwargs
        )

    def __call__(self, **sample):
        result = self.generator(**{k: v for k, v in sample.items() if k != "requirement"}, requirement=self.requirement)
        return EvalResult(
            field=self.field,
            requirement=self.requirement,
            evaluation_result=result["evaluation_result"],
            reason=result["reason"]
        )
