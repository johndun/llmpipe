from dataclasses import dataclass
from typing import Dict, List

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class NotInBlockedList(Evaluation):
    """Ensure that a field is not in a blocked list

    Usage:

    ```python
    blocked_list1 = NotInBlockedList(field="color", blocked_list=["green"])
    print(blocked_list1(color="black"))
    print(blocked_list1(color="green"))

    blocked_list2 = NotInBlockedList(field="color", blocked_list_field="bad_colors")
    print(blocked_list2(color="black", bad_colors=["green"]))
    print(blocked_list2(color="green", bad_colors=["green"]))
    ```
    """
    blocked_list: List[str] = None
    blocked_list_field: str = None
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement and self.blocked_list and not self.blocked_list_field:
            self.requirement = f"Is not identical to any of the following blocked values: {', '.join(self.blocked_list)}"
        elif not self.requirement and not self.blocked_list and self.blocked_list_field:
            self.requirement = "Is not identical to any of the following blocked values: {{" + self.blocked_list_field + "}}"

    def __call__(self, **inputs) -> EvalResult:
        slash_pattern = r'\b\w+/\w+\b'
        text = inputs[self.field].lower().strip()
        blocked_list = self.blocked_list.copy() if self.blocked_list else []
        if self.blocked_list_field is not None and self.blocked_list_field in inputs:
            blocked_list += inputs[self.blocked_list_field]

        blocked_list = [x.lower().strip() for x in blocked_list]

        if text in blocked_list:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"'{text}' is one of the blocked values"
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")