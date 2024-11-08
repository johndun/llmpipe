from dataclasses import dataclass, field, asdict
from typing import List, Union, Dict

from llmpipe.evaluations import deterministic_eval_factory, Evaluation


@dataclass
class Field:
    """Defines an LLM module input or output"""
    name: str  #: A name for the field
    description: str  #: Description for the field
    evaluations: List[Evaluation] = field(default_factory=lambda: [])  #: Field evaluations
    inputs: List['Field'] = field(default_factory=lambda: [])  #: Inputs needed to generate this field

    def __post_init__(self):
        if self.inputs:
            self.inputs = [Field(**x) for x in self.inputs]

        if self.evaluations:
            self.evaluations = [
                deterministic_eval_factory(field=self.name, **x)
                for x in self.evaluations
            ]

    @property
    def markdown(self) -> str:
        """Apply markdown formatting to the input name"""
        return f"`{self.name}`"

    @property
    def xml(self) -> str:
        """Apply xml formatting to the input name"""
        return f"<{self.name}>"

    @property
    def xml_close(self) -> str:
        """Apply xml formatting to the input name"""
        return f"</{self.name}>"

    @property
    def definition(self) -> str:
        """Return a formatted definition string"""
        return f"{self.name}: {self.description}"

    @property
    def input_template(self) -> str:
        """Returns an input template using xml tags and double curly braces"""
        return self.xml + "\n{{" + self.name + "}}\n" + self.xml_close
