from dataclasses import dataclass

from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class MaxWords(Evaluation):
    """Evaluates a field for a maximum number of words requirement"""
    max_words: int = 10
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement:
            self.requirement = f"Has at most {self.max_words} words"

    def __call__(self, **inputs):
        input = inputs[self.field]
        word_count = len(input.split())
        if word_count <= self.max_words:
            return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
        else:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"Should have at most {self.max_words} words, but has {word_count}"
            )
