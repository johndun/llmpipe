import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict

from datasets import Dataset

from llmpipe.field import Input, Output, output_factory
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml_utils import parse_text_for_one_tag


logger = logging.getLogger(__name__)


@dataclass
class PromptModule(LlmChat):
    """An LLM prompt class
    """
    inputs: List[Input] = field(default_factory=lambda: [])  #: Prompt inputs. If not provided, will be inherited from `outputs`.
    outputs: List[Output] = field(default_factory=lambda: [])  #: Prompt outputs
    inputs_header: str = "You will be provided the following inputs:"  #: The inputs definition section header
    outputs_header: str = "Generate the following outputs within XML tags:"  #: The outputs definition section header
    task: str = ""  #: The task description at the top of the prompt
    details: str = ""  #: Task details that come after the input output definition sections
    verbose: bool = False  #: If true, print additional LLM output to stdout

    def __post_init__(self):
        super().__post_init__()
        # Initialize output classes when dictionary is provided
        self.outputs = [
            output_factory(**x) if isinstance(x, dict) else x
            for x in self.outputs
        ]
        # Infer inputs from the outputs when not inputs are not defined
        if not self.inputs:
            inputs = {}
            for output in self.outputs:
                for inp in output.inputs:
                    inputs[inp.name] = inp
            self.inputs = list(inputs.values())
        # Initialize input classes when dictionary is provided
        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

    @property
    def prompt(self) -> str:
        """Returns a prompt for generating the output"""
        prompt = ["## Task Description"]

        if self.task:
            prompt.append(self.task)

        if self.inputs:
            prompt.append(self.inputs_header)
            for x in self.inputs:
                prompt.append(x.definition)

        prompt.append(self.outputs_header)
        for x in self.outputs:
            prompt.append(x.definition)

        if self.details:
            prompt.append("### Details")
            prompt.append(self.details)

        if self.inputs:
            prompt.append("## Inputs")
            for x in self.inputs:
                prompt.append(x.input_template)

        return "\n\n".join(prompt)

    def verify_outputs(self, outputs):
        assert set([x.name for x in self.outputs]) <= set(outputs.keys())

    def forward_one(self, **inputs) -> Dict:
        self.clear_history()

        try:
            if self.verbose:
                response_text = ""
                for chunk in self._call_stream(prompt=Template(self.prompt).format(**inputs)):
                    print(chunk, flush=True, end="")
                    response_text += chunk
                print()
            else:
                response_text = self._call(prompt=Template(self.prompt).format(**inputs))
            logger.info(f"PromptModule response: {response_text}")
            logger.info(f"Token counts - Last: {self.tokens.last}, Total: {self.tokens.total}")
        except Exception as e:
            print(e)
            response_text = ""

        outputs = {}
        for field in self.outputs:
            try:
                outputs[field.name] = field.process(
                    parse_text_for_one_tag(response_text, field.name).strip()
                )
            except Exception as e:
                print(e)
                outputs[field.name] = None

        self.verify_outputs(outputs)

        if self.verbose:
            print(f"Tokens used: {self.tokens.total}")
        return outputs

    def __call__(self, num_proc: int = 1, **inputs) -> Dict:
        if not inputs or not isinstance(list(inputs.values())[0], list):
            return self.forward_one(**inputs)

        return (
            Dataset.from_dict(inputs)
            .map(
                lambda sample: sample | self.forward_one(**sample),
                num_proc=num_proc,
                batched=False
            )
        ).to_dict()
