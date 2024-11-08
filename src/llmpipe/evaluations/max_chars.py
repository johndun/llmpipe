from dataclasses import dataclass

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class MaxCharacters(Evaluation):
    """Evaluates a field for a maximum number of characters requirement"""
    max_chars: int = 50

    def __post_init__(self):
        if not self.requirement:
            self.requirement = f"Has at most {self.max_chars} characters"

    def __call__(self, **inputs):
        input = inputs[self.field]
        this_len = len(input)
        if this_len <= self.max_chars:
            return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
        else:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"Should have at most {self.max_chars} chars, but has {this_len}"
            )
