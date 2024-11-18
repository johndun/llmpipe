from dataclasses import dataclass
from typing import List

from ..evaluations.core import Evaluation, EvalResult


@dataclass
class ContainsOne(Evaluation):
    """Evaluates whether a field contains at least one of the specified values.

    Args:
        field: The field to evaluate
        value: List of values where at least one must be present
        requirement: The requirement being evaluated
        type: The type of evaluation
        label: Optional label for the evaluation
    """
    required_terms: List[str] = None
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        assert self.required_terms
        if not self.requirement:
            self.requirement = f"Must contain at least one of: " + ", ".join([str(x) for x in self.required_terms])

    def __call__(self, **inputs) -> EvalResult:
        """Check if field contains at least one of the required values.

        Args:
            **inputs: Dictionary containing the field to evaluate

        Returns:
            EvalResult with pass/fail and explanation
        """
        field_value = str(inputs.get(self.field, "")).lower()
        
        for required in self.required_terms:
            if str(required).lower() in field_value:
                return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")

        reason = f"Field '{self.field}' does not contain any of the required values: {self.required_terms}"
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="FAIL", reason=reason)
