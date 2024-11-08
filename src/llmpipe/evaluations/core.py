from dataclasses import dataclass


@dataclass
class EvalResult:
    """An evaluation result"""
    field: str  #: The field that the evaluation applies to
    requirement: str  #: A brief description of the requirement
    evaluation_result: str  #: The evaluation result, e.g., 'PASS' or 'FAIL'
    reason: str = ""  #: An optional reason for the evaluation


@dataclass
class Evaluation:
    """A single field evaluation"""
    field: str  #: The field that the evaluation applies to
    requirement: str  #: A brief description of the requirement
    type: str  #: The evaluation type, e.g., 'deterministic' or 'llm'

    def __call__(self, **inputs) -> EvalResult:
        raise NotImplementedError
