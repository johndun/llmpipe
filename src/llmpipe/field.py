from dataclasses import dataclass, field, asdict
from typing import List, Union, Dict

from llmpipe.evaluations import deterministic_eval_factory, Evaluation


@dataclass
class Input:
    """Defines an LLM module input or output"""
    name: str  #: A name for the field
    description: str  #: Description for the field

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


@dataclass
class Output(Input):
    """Defines an LLM module input or output with evaluations and linked inputs"""
    evaluations: List[Evaluation] = field(default_factory=lambda: [])  #: Field evaluations
    inputs: List[Input] = field(default_factory=lambda: [])  #: Inputs needed to generate this field

    def __post_init__(self):
        if self.inputs and not isinstance(self.inputs[0], Input):
            self.inputs = [Input(**x) for x in self.inputs]

        if self.evaluations and not isinstance(self.evaluations[0], Evaluation):
            self.evaluations = [
                deterministic_eval_factory(field=self.name, **x)
                for x in self.evaluations
            ]