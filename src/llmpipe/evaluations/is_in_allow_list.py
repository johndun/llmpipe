from dataclasses import dataclass
from typing import Dict, List

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class IsInAllowList(Evaluation):
    """Ensure that a field contains only allowed terms"""
    allowed_terms: List[str] = None
    allowed_terms_field: str = None 
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement and self.allowed_terms and not self.allowed_terms_field:
            self.requirement = f"Must be one of the following terms: {', '.join(self.allowed_terms)}"
        elif not self.requirement and not self.allowed_terms and self.allowed_terms_field:
            self.requirement = "Must be one of the following terms: {{" + self.allowed_terms_field + "}}"

    def __call__(self, **inputs) -> EvalResult:
        text = inputs[self.field].lower()
        allowed_terms = self.allowed_terms.copy() if self.allowed_terms else []
        if self.allowed_terms_field is not None and self.allowed_terms_field in inputs:
            allowed_terms += inputs[self.allowed_terms_field] or []
        
        # Convert allowed terms to lowercase for case-insensitive comparison
        allowed_terms = [term.lower() for term in allowed_terms]
        
        if text not in allowed_terms:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"'{inputs[self.field]}' is not in the list of allowed terms"
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
