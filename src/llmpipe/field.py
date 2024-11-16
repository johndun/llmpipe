from dataclasses import dataclass, field, asdict
from typing import List, Union, Dict

from llmpipe.evaluations import eval_factory, Evaluation


@dataclass
class Input:
    """Defines an LLM module input or output"""
    name: str  #: A name for the field
    description: str = ""  #: Description for the field

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
    """Defines an LLM module input or output with evaluations and linked inputs

    Evaluations should be dictionaries with keys:

        type (str): The type of evaluation to create
        value (Union[int, float, str]): Initialization parameter to pass to the Evaluation subclass
        label (str): A brief description of the requirement
        **kwargs: Keyword arguments passed to `LlmEvaluation`
    
    """
    evaluations: List[Dict] = field(default_factory=lambda: [])  #: Field evaluations
    inputs: List[Input] = field(default_factory=lambda: [])  #: Inputs needed to evaluate this field

    def __post_init__(self):
        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

        # Convert any dict evaluations to Evaluation objects
        self.evaluations = [
            eval_factory(
                field=self.name,
                field_description=self.description,
                inputs=x["inputs"] if "inputs" in x else self.inputs,
                **{k: v for k, v in x.items() if k != "inputs"}
            ) if isinstance(x, dict) else x
            for x in self.evaluations
        ]
