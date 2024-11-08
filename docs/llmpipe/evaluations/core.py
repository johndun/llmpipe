from dataclasses import dataclass


@dataclass
class EvalResult:
    """An evaluation result"""
    field: str  #: Field that the evaluation result applies to
    requirement: str  #: A brief description of the requirement
    evaluation_result: str  #: The result, e.g., 'PASS' or 'FAIL'
    reason: str = ""  #: An optional reason for the evaluation


@dataclass
class Evaluation:
    """An evaluation"""
    field: str  #: Field that the evaluation applies to
    requirement: str  #: A brief description of the requirement
    type: str  #: The type of evaluation, e.g., deterministic or llm

    def __call__(self, **inputs) -> EvalResult:
        raise NotImplementedError
