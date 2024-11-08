from dataclasses import dataclass
from typing import Dict, List

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class NoBlockedTerms(Evaluation):
    """Ensure that a field contains no blocked terms"""
    blocked_terms: List[str] = None
    blocked_terms_field: str = None
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement and self.blocked_terms and not self.blocked_terms_field:
            self.requirement = f"Does not contain any of the following: {', '.join(self.blocked_terms)}"
        elif not self.requirement and not self.blocked_terms and self.blocked_terms_field:
            self.requirement = "Does not contain any of the following: {{" + self.blocked_terms_field + "}}"

    def __call__(self, **inputs) -> EvalResult:
        text = inputs[self.field]
        words = text.lower().split()
        matches = []
        blocked_terms = self.blocked_terms.copy() if self.blocked_terms else []
        if self.blocked_terms_field is not None and self.blocked_terms_field in inputs:
            blocked_terms += inputs[self.blocked_terms_field] or []
        for term in blocked_terms:
            if len(term.split()) == 1 and term.lower() in words:
                matches.append(term)
            elif len(term.split()) > 1 and term.lower() in text:
                matches.append(term)
        if matches:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"Should not contain the blocked text: {', '.join(matches)}"
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
