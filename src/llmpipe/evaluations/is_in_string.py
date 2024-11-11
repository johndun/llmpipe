from dataclasses import dataclass
from typing import Dict

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class IsInString(Evaluation):
    """Ensure that a field is contained within a target string
    
    Usage:
    
    ```python
    # Using direct string
    in_string1 = IsInString(field="word", target_string="The quick brown fox")
    print(in_string1(word="quick"))  # PASS
    print(in_string1(word="slow"))   # FAIL
    
    # Using field reference
    in_string2 = IsInString(field="word", target_string_field="text")
    print(in_string2(word="dog", text="The dog barks"))  # PASS
    print(in_string2(word="cat", text="The dog barks"))  # FAIL
    ```
    """
    target_string: str = None
    target_string_field: str = None
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement:
            if self.target_string and not self.target_string_field:
                self.requirement = f"Must be contained in: {self.target_string}"
            elif not self.target_string and self.target_string_field:
                self.requirement = "Must be contained in: {{" + self.target_string_field + "}}"

    def __call__(self, **inputs) -> EvalResult:
        text = inputs[self.field].lower()
        target = self.target_string or ""
        
        if self.target_string_field is not None and self.target_string_field in inputs:
            target = inputs[self.target_string_field] or ""
            
        # Convert target to lowercase for case-insensitive comparison
        target = target.lower()
        
        if text not in target:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"'{inputs[self.field]}' is not found in the target string"
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
