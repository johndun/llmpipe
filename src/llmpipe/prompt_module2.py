import json
import logging
import yaml
from dataclasses import dataclass, field, asdict
from typing import Annotated, List, Dict

import typer
import polars as pl
from datasets import Dataset
from typer import Option, Argument

from llmpipe.data import read_data, write_data
from llmpipe.field import Input, Output, output_factory
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml_utils import parse_text_for_one_tag


logger = logging.getLogger(__name__)


@dataclass
class PromptModule2(LlmChat):
    """An LLM prompt class
    """
    task: str = "" #: The task description at the top of the prompt
    outputs: List[Output] = field(default_factory=lambda: [])  #: Prompt outputs
    inputs: List[Input] = field(default_factory=lambda: [])  #: Prompt inputs.
    outputs_header: str = "Generate the following outputs enclosed within XML tags:"  #: The outputs definition section header
    verbose: bool = False  #: If true, print additional LLM output to stdout
    footer: str = None  #: An optional prompt footer (text for the very end of the prompt)

    def __post_init__(self):
        super().__post_init__()
        assert self.task and self.outputs
        # Initialize output classes when dictionary is provided
        self.outputs = [
            output_factory(**x) if isinstance(x, dict) else x
            for x in self.outputs
        ]
        # Initialize input classes when dictionary is provided
        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

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
                inline = f"{self.outputs[0].xml}...{self.outputs[0].xml_close}"
                self.footer = f"Generate the required output within XML tags: {inline}"

    @property
    def prompt(self) -> str:
        """Returns a prompt for generating the output"""
        prompt = [self.task]

        if self.inputs:
            for x in self.inputs:
                prompt.append(x.input_template)

        prompt.append(self.outputs_header)
        for x in self.outputs:
            prompt.append(x.definition)

        prompt.append(self.footer)

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


def run_yaml_prompt(
        prompt_path: Annotated[str, Option(help="Path to a yaml file containing the prompt configuration")] = None,
        input_data_path: Annotated[str, Option(help="Dataset to run prompt on")] = None,
        output_data_path: Annotated[str, Option(help="Path to save processed dataset")] = None,
        num_proc: Annotated[int, Option(help="Number of processes to use is dataset mode")] = 1,
        n_samples: Annotated[int, Option(help="Optional maximum number of samples to run")] = None,
        verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
        model: Annotated[str, Option(help="A LiteLLM model identifier")] = None
):
    """Run a prompt on a dataset."""

    # Read the prompt
    with open(prompt_path, "r") as f:
        prompt_config = yaml.safe_load(f.read())

    # Initialize the prompt
    prompt_config["model"] = model
    prompt_config["verbose"] = verbose
    prompt = PromptModule2(**prompt_config)
    if verbose:
        print(prompt.prompt)

    # Read the data
    samples = read_data(input_data_path)

    # Sample if requested
    if n_samples is not None:
        n_samples = min(n_samples, len(samples))
        samples = random.sample(samples, n_samples)

    # Run prompt and return results
    data = pl.from_dicts(samples).to_dict(as_series=False)
    samples = pl.from_dict(prompt(**data, num_proc=num_proc)).to_dicts()

    # Write the output to the target output file location
    write_data(samples, output_data_path)


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(run_yaml_prompt)
    app()