import re
from dataclasses import dataclass

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class NoLongWords(Evaluation):
    """Evaluates that a field has no words with more than `max_chars` characters

    Usage:

    ```python
    no_long_words = NoLongWords(field="text", max_chars=9)
    print(no_long_words(text="A vegetarian nightingale"))
    print(no_long_words(text="cat dog"))
    ```
    """
    max_chars: int = 10
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement:
            self.requirement = f"Contains no words with more than {self.max_chars} characters"

    def __call__(self, **inputs) -> EvalResult:
        text = inputs[self.field]
        too_long_words = []
        for word in text.split():
            if len(word) > self.max_chars:
                too_long_words.append(word)
        if too_long_words:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"The following words have more than {self.max_chars} characters: {', '.join(too_long_words)}"
            )

        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
