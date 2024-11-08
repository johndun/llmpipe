from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class EvalResult:
    """Result of an evaluation containing a score and optional metadata"""
    score: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not 0 <= self.score <= 1:
            raise ValueError("Score must be between 0 and 1")

@dataclass
class Evaluation:
    """Base class for implementing evaluations
    
    Subclass this to implement custom evaluation logic.
    """
    name: str
    description: str = ""

    def __call__(self, **inputs) -> EvalResult:
        """Run the evaluation on the given inputs
        
        Args:
            **inputs: Keyword arguments for the evaluation
            
        Returns:
            EvalResult containing score and metadata
        """
        raise NotImplementedError("Subclasses must implement __call__")
