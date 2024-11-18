from dataclasses import dataclass, field
from typing import List, Union

from ..evaluations.core import Evaluation, EvalResult


@dataclass
class ContainsAll(Evaluation):
    """Evaluates whether a field contains all specified values.

    Args:
        field: The field to evaluate
        value: List of values that must all be present
        requirement: The requirement being evaluated
        type: The type of evaluation
        label: Optional label for the evaluation
    """
    required_terms: List[str] = field(default_factory=lambda: [])
    requirement: str = None
    type: str = "deterministic"

    def __call__(self, **inputs) -> EvalResult:
        """Check if field contains all required values.

        Args:
            **inputs: Dictionary containing the field to evaluate

        Returns:
            EvalResult with pass/fail and explanation
        """
        field_value = str(inputs.get(self.field, "")).lower()
        missing = []

        for required in self.required_terms:
            if str(required).lower() not in field_value:
                missing.append(required)

        passed = len(missing) == 0
        
        if passed:
            return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")

        reason = f"Field '{self.field}' is missing required values: {missing}"
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="FAIL", reason=reason)

