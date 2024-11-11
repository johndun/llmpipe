import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict

from llmpipe.field import Input, Output
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml import parse_text_for_tag
from llmpipe.llmprompt import LlmPrompt


logger = logging.getLogger(__name__)


@dataclass
class LlmPromptForMany(LlmChat):
    """An LLM prompt class that returns a list of outputs"""
    inputs: List[Input] = field(default_factory=lambda: [])  #: Prompt inputs
    output: Output = None  #: The output
    inputs_header: str = "You are provided the following inputs:"  #: The inputs definition section header
    task: str = ""  #: The task description at the top of the prompt
    details: str = ""  #: Task details that come after the input output definition sections
    footer: str = None  #: An optional prompt footer (text for the very end of the prompt)
    cot_string: str = "Begin by thinking step by step"


    def __post_init__(self):
        assert self.output is not None
        super().__post_init__()
        if self.footer is None:
            inline = f"{self.output.xml}...{self.output.xml_close}"
            if self.cot_string:
                self.footer = f"Generate the required outputs within XML tags:\n<thinking>...</thinking>\n{inline}\n{inline}\n..."
            else:
                self.footer = f"Generate the required outputs within XML tags:\n{inline}\n{inline}\n..."

    @property
    def prompt(self) -> str:
        """Returns a prompt for generating the output"""
        prompt = ["# Task Description"]

        if self.inputs:
            prompt.append(self.inputs_header)
            prompt.append("\n".join([f"- {x.definition}" for x in self.inputs]))

        if self.task:
            prompt.append(self.task)

        prompt.append("Generate the following outputs enclosed within XML tags:")

        if self.cot_string:
            cot = Output("thinking", "Begin by thinking step by step")
            prompt.append(f"{cot.xml}\n{cot.description}\n{cot.xml_close}")

        prompt.append(f"{self.output.xml}\n{self.output.description}\n{self.output.xml_close}")

        if self.output.evaluations:
            prompt.append(f"Requirements for {self.output.markdown}:")
            prompt.append("\n".join([f"- {evl.requirement}" for evl in self.output.evaluations]))

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
        assert self.output.name in set(outputs.keys())

    def __call__(self, **inputs) -> List[Dict]:
        self.clear_history()

        try:
            response_text = self._call(prompt=Template(self.prompt).format(**inputs))
            logger.info(f"LlmPrompt response: {response_text}")
            logger.info(f"Token counts - Last: {self.tokens.last}, Total: {self.tokens.total}")
        except Exception as e:
            print(e)
            response_text = ""

        outputs = {
            self.output.name: [x.strip() for x in parse_text_for_tag(response_text, self.output.name)]
        }
        self.verify_outputs(outputs)
        return outputs

    def _evaluate(self, break_after_first_fail: bool = False, **inputs) -> Dict:
        """Run evaluations"""
        outputs = {}
        field = self.output
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
                if break_after_first_fail:
                    break

        outputs[f"{field.name}_eval"] = evaluation_results
        return outputs

    def evaluate(self, break_after_first_fail: bool = False, **inputs) -> List[Dict]:
        input_keys = [x.name for x in self.inputs]
        orig_inputs = {k: v for k, v in inputs.items() if k in input_keys}
        inputs = [
            orig_inputs | {self.output.name: x}
            for x in inputs[self.output.name]
        ]
        eval_results = [self._evaluate(**x, break_after_first_fail=break_after_first_fail) for x in inputs]
        return {f"{self.output.name}_eval": [x[f"{self.output.name}_eval"] for x in eval_results]}

    def discard(self, **inputs: List[Dict]) -> List[Dict]:
        eval_results = self.evaluate(**inputs, break_after_first_fail=True)
        return {
            self.output.name: [
                x
                for x, evl in zip(inputs[self.output.name], eval_results[f"{self.output.name}_eval"])
                if not len(evl)
            ]
        }

    def _revise(self, max_revisions: int = 6, **inputs) -> Dict:
        """Evaluate and revise"""
        # Iterate max_revision times or until all evaluations pass
        for revision_idx in range(max_revisions + 1):
            eval_results = self._evaluate(**inputs, break_after_first_fail=True)

            field = self.output
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
            eval_results_str = json.dumps(eval_result[0], indent=2)
            logger.info(f"Revision {revision_idx + 1}: `{field.name}`")
            revised = revisor(**inputs, evaluation_result=eval_results_str)
            if revised[field.name].strip():
                inputs[field.name] = revised[field.name].strip()

        return inputs

    def revise(self, max_revisions: int = 6, **inputs) -> List[Dict]:
        input_keys = [x.name for x in self.inputs]
        orig_inputs = {k: v for k, v in inputs.items() if k in input_keys}
        inputs = [
            orig_inputs | {self.output.name: x}
            for x in inputs[self.output.name]
        ]
        revised_results = [self._revise(**x, max_revisions=max_revisions) for x in inputs]
        return {self.output.name: [x[self.output.name] for x in revised_results]}
