from dataclasses import dataclass, field
from typing import List, Dict

from llmpipe.field import Input, Output
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml import parse_text_for_one_tag


@dataclass
class LlmPrompt(LlmChat):
    """An LLM prompt class

    Constructions a prompt template using the input and output fields.
    """
    inputs: List[Input] = field(default_factory=lambda: [])  #: Prompt inputs
    outputs: List[Output] = field(default_factory=lambda: [])  #: Prompt outputs
    inputs_header: str = "You are provided the following inputs:"  #: The inputs definition section header
    task: str = ""  #: The task description at the top of the prompt
    details: str = ""  #: Task details that come after the input output definition sections
    footer: str = None  #: An optional prompt footer (text for the very end of the prompt)

    def __post_init__(self):
        super().__post_init__()
        if self.footer is None:
            if len(self.outputs) == 0:
                self.footer = ""
            elif len(self.outputs) > 2:
                inline = ", ".join([f"{x.xml}...{x.xml_close}" for x in self.outputs])
                self.footer = f"Generate the required outputs within XML tags: {inline}"
            elif len(self.outputs) == 2:
                inline = " and ".join([f"{x.xml}...{x.xml_close}" for x in self.outputs])
                self.footer = f"Generate the required outputs within XML tags: {inline}"
            else:
                inline = self.outputs[0].xml
                self.footer = f"Generate the required output within XML tags: {inline}"

    @property
    def prompt(self) -> str:
        """Returns a prompt for generating the output"""
        prompt = ["# Task Description"]

        if self.inputs:
            prompt.append(self.inputs_header)
            prompt.append("\n".join([f"- {x.definition}" for x in self.inputs]))

        if self.task:
            prompt.append(self.task)

        prompt.append("Generate the following outputs within XML tags:")
        for idx, x in enumerate(self.outputs):
            prompt.append(f"{x.xml}\n{x.description}\n{x.xml_close}")
        for x in self.outputs:
            if x.evaluations:
                prompt.append(f"Requirements for {x.markdown}:")
                prompt.append("\n".join([f"- {evl.requirement}" for evl in x.evaluations]))

        if self.details:
            prompt.append(self.details)

        if self.inputs:
            prompt.append("# Inputs")
            for x in self.inputs:
                prompt.append(x.input_template)

        if self.footer:
            prompt.append(self.footer)

        return "\n\n".join(prompt)

    def verify_outputs(self, outputs):
        assert set([x.name for x in self.outputs]) <= set(outputs.keys())

    def __call__(self, **inputs) -> Dict:
        self.clear_history()
        try:
            response_text = self._call(prompt=Template(self.prompt).format(**inputs))
        except Exception as e:
            print(e)
            response_text = ""

        outputs = {}
        for field in self.outputs:
            outputs[field.name] = parse_text_for_one_tag(response_text, field.name).strip()

        self.verify_outputs(outputs)
        return outputs
