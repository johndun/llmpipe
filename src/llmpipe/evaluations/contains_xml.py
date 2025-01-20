from dataclasses import dataclass
from typing import Dict, List

from llmpipe.xml_utils import parse_text_for_tags
from llmpipe.evaluations.core import Evaluation, EvalResult


@dataclass
class ContainsXml(Evaluation):
    """Ensure that a field contains XML blocks."""
    xml_tags: List[str] = None
    requirement: str = None
    type: str = "deterministic"

    def __post_init__(self):
        if not self.requirement:
            self.requirement = f"Must contain the following XML blocks: " + ", ".join(["<" + x + ">" for x in self.xml_tags])

    def __call__(self, **inputs) -> EvalResult:
        text = inputs[self.field]
        all_tags = [x.tag for x in parse_text_for_tags(text)]
        missing_tags = []
        for tag in self.xml_tags:
            if tag not in all_tags:
                missing_tags.append(tag)
        if missing_tags:
            return EvalResult(
                field=self.field,
                requirement=self.requirement,
                evaluation_result="FAIL",
                reason=f"The following required XML blocks are missing: " + ", ".join(["<" + x + ">" for x in missing_tags])
            )
        return EvalResult(field=self.field, requirement=self.requirement, evaluation_result="PASS")
