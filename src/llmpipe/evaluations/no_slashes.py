import re
from dataclasses import dataclass

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class NoSlashes(Evaluation):
    """Ensure that a field contains no slash/constructions"""
    requirement: str = "Does not contain any slash/constructions"
    type: str = "deterministic"

    def __call__(self, **inputs):
        input = inputs[self.field]
        slash_pattern = r'\b\w+/\w+\b'
        matches_with_slashes = re.findall(slash_pattern, input)

        if matches_with_slashes:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"`{self.field}` should not contain slash constructions: {', '.join(matches_with_slashes)}"
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")