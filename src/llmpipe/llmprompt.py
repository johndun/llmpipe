import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict

from llmpipe.field import Input, Output
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml import parse_text_for_one_tag


logger = logging.getLogger(__name__)


@dataclass
class LlmPrompt(LlmChat):
    """An LLM prompt class

    - Constructions a prompt template using the input and output fields.
    - Any Evaluations associated with the outputs will be executed. Non-passing evaluations will be returned.
    - Non-llm evals will be run first.
    """
    inputs: List[Input] = field(default_factory=lambda: [])  #: Prompt inputs
    outputs: List[Output] = field(default_factory=lambda: [])  #: Prompt outputs
    inputs_header: str = "You are provided the following inputs:"  #: The inputs definition section header
    task: str = ""  #: The task description at the top of the prompt
    details: str = ""  #: Task details that come after the input output definition sections
    footer: str = None  #: An optional prompt footer (text for the very end of the prompt)
    break_after_first_fail: bool = True  #: If true, returns only the 1st failed evaluation

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
                inline = f"{self.outputs[0].xml}...{self.outputs[0].xml_close}"
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
            logger.info(f"LlmPrompt response: {response_text}")
            logger.info(f"Token counts - Last: {self.tokens.last}, Total: {self.tokens.total}")
        except Exception as e:
            print(e)
            response_text = ""

        outputs = {}
        for field in self.outputs:
            outputs[field.name] = parse_text_for_one_tag(response_text, field.name).strip()

        self.verify_outputs(outputs)
        return outputs

    def evaluate(self, **inputs) -> Dict:
        """Run evaluations"""
        outputs = {}

        for field in self.outputs:
            # Initialize separate deterministic and llm-based evaluations
            deterministic_evaluations = []
            llm_evaluations = []
            for evaluation in field.evaluations or []:
                if evaluation.type == "llm":
                    llm_evaluations.append(evaluation)
                else:
                    deterministic_evaluations.append(evaluation)

            evaluation_results = []
            for evaluation in deterministic_evaluations + llm_evaluations:
                eval_result = evaluation(**(inputs | outputs))
                if eval_result.evaluation_result != "PASS":
                    evaluation_results.append(asdict(eval_result))
                    if self.break_after_first_fail:
                        break

            outputs[f"{field.name}_eval"] = evaluation_results
        return outputs

    def revise(self, max_revisions: int = 6, **inputs) -> Dict:
        """Evaluate and revise"""
        outputs = {}
        # Iterate max_revision times or until all evaluations pass
        for revision_idx in range(max_revisions + 1):
            eval_results = self.evaluate(**inputs)

            for field in self.outputs:
                eval_result = eval_results.get(f"{field.name}_eval")
                if not eval_result:
                    continue
                chain_of_thought = Output("thinking", "Begin by thinking step by step")
                evaluation_result = Input("evaluation_result", "An evaluation result")
                revisor = LlmPrompt(
                    inputs_header="You will be provided a set of inputs, along with a non-passing evaluation result.",
                    task="Your task is to generate an updated version of the field indicated in the evaluation result so that it meets all evaluation criteria and requirements.",
                    details=self.details,
                    inputs=field.inputs + [field, evaluation_result],
                    outputs=[chain_of_thought, field],
                    **self.model_args
                )
                print(revisor.prompt)
                eval_results_str = json.dumps(eval_result[0], indent=2)
                logger.info(f"Revision {revision_idx + 1}: `{field.name}`")
                revised = revisor(**inputs, evaluation_result=eval_results_str)
                if revised[field.name].strip():
                    outputs[field.name] = revised[field.name].strip()

        return outputs