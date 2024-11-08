import re
from dataclasses import dataclass

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class NoSquareBrackets(Evaluation):
    """Ensure that a field contains no square bracket [placeholders]"""
    requirement: str = "Does not contain square bracket [placeholders]"
    type: str = "deterministic"

    def __call__(self, **inputs):
        input = inputs[self.field]
        brackets_pattern = r'\[.*?\]'
        matches_with_brackets = re.findall(brackets_pattern, input)

        if matches_with_brackets:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"Should not contain square brackets: {', '.join(matches_with_brackets)}"
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
