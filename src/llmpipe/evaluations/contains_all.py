from dataclasses import dataclass
from typing import List, Union

from ..evaluations.core import Evaluation, EvalResult


@dataclass
class ContainsAll(Evaluation):
    """Evaluates whether a field contains all specified values."""
    required_terms: List[str] = None
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        assert self.required_terms
        if not self.requirement:
            self.requirement = f"Must contain the following terms: " + ", ".join([str(x) for x in self.required_terms])

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

