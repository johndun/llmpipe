from dataclasses import dataclass
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

    field: str
    value: List[str]
    requirement: str
    type: str
    label: str = None

    def __call__(self, **inputs) -> EvalResult:
        """Check if field contains all required values.

        Args:
            **inputs: Dictionary containing the field to evaluate

        Returns:
            EvalResult with pass/fail and explanation
        """
        field_value = str(inputs.get(self.field, "")).lower()
        missing = []

        for required in self.value:
            if str(required).lower() not in field_value:
                missing.append(required)

        passed = len(missing) == 0
        
        if passed:
            explanation = f"Field '{self.field}' contains all required values: {self.value}"
        else:
            explanation = f"Field '{self.field}' is missing required values: {missing}"

        return EvalResult(
            passed=passed,
            explanation=explanation
        )
