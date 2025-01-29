import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict

from llmpipe.field import Input, Output
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml_utils import parse_text_for_one_tag


logger = logging.getLogger(__name__)


@dataclass
class LlmPrompt(LlmChat):
    """An LLM prompt class

    - Constructions a prompt template using the input and output fields.
    - Any Evaluations associated with the outputs will be executed. Non-passing evaluations will be returned.
    - Non-llm evals will be run first.
    """
    inputs: List[Input] = field(default_factory=lambda: [])  #: Prompt inputs. If not provided, will be inherited from `outputs`.
    outputs: List[Output] = field(default_factory=lambda: [])  #: Prompt outputs
    inputs_header: str = "You are provided the following inputs:"  #: The inputs definition section header
    outputs_header: str = "Generate the following outputs within XML tags:"  #: The outputs definition section header
    task: str = ""  #: The task description at the top of the prompt
    details: str = ""  #: Task details that come after the input output definition sections
    footer: str = None  #: An optional prompt footer (text for the very end of the prompt)
    include_evals_in_prompt: bool = True  #: Whether to include evaluation requirements in the prompt
    verbose: bool = False  #: If true, print additional LLM output to stdout

    def __post_init__(self):
        super().__post_init__()

        self.outputs = [
            Output(**x) if isinstance(x, dict) else x
            for x in self.outputs
        ]

        if not self.inputs:
            inputs = {}
            for output in self.outputs:
                for inp in output.inputs:
                    inputs[inp.name] = inp
            self.inputs = list(inputs.values())

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
        prompt = ["# Task Description"]

        if self.inputs:
            prompt.append(self.inputs_header)
            prompt.append("\n".join([f"- {x.definition}" for x in self.inputs]))

        if self.task:
            prompt.append(self.task)

        prompt.append(self.outputs_header)
        for idx, x in enumerate(self.outputs):
            prompt.append(f"{x.xml}\n{x.description}\n{x.xml_close}")
        if self.include_evals_in_prompt:
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
            if self.verbose:
                response_text = ""
                for chunk in self._call_stream(prompt=Template(self.prompt).format(**inputs)):
                    print(chunk, flush=True, end="")
                    response_text += chunk
                print()
            else:
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

        if self.verbose:
            print(f"Tokens used: {self.tokens.total}")
        return outputs

    def evaluate(self, break_after_first_fail: bool = False, **inputs) -> Dict:
        """Run evaluations"""
        outputs = {}

        for field in self.outputs:
            # Initialize separate deterministic and llm-based evaluations
            deterministic_evaluations = []
            llm_evaluations = []
            for evaluation in field.evaluations or []:
                if evaluation.type == "llm":
                    evaluation.generator.model = self.model
                    evaluation.generator.verbose = self.verbose
                    llm_evaluations.append(evaluation)
                else:
                    deterministic_evaluations.append(evaluation)

            evaluation_results = []
            for evaluation in deterministic_evaluations + llm_evaluations:
                eval_result = evaluation(**(inputs | outputs))
                if evaluation.type == "llm":
                    self.tokens += evaluation.tokens
                if eval_result.evaluation_result != "PASS":
                    evaluation_results.append(asdict(eval_result))
                    if break_after_first_fail:
                        break

            outputs[f"{field.name}_eval"] = evaluation_results
        return outputs

    def revise(self, max_revisions: int = 6, **inputs) -> Dict:
        """Evaluate and revise"""
        # Iterate max_revision times or until all evaluations pass
        for revision_idx in range(max_revisions + 1):
            finished = True
            eval_results = self.evaluate(**inputs, break_after_first_fail=True)

            for field in self.outputs:
                if self.verbose:
                    print(f"Revision iteration {revision_idx + 1} for `{field.name}`")
                eval_result = eval_results.get(f"{field.name}_eval")
                if not eval_result:
                    continue
                if self.verbose:
                    print("Revising for: " + str(eval_result))
                finished = False
                chain_of_thought = Output("thinking", "Begin by thinking step by step")
                evaluation_result = Input("evaluation_result", "An evaluation result")
                revisor = LlmPrompt(
                    inputs_header="You will be provided a set of inputs, along with a non-passing evaluation result.",
                    task="Your task is to generate an updated version of the field indicated in the evaluation result so that it meets all evaluation criteria and requirements.",
                    details=self.details,
                    inputs=self.inputs + [field, evaluation_result],
                    outputs=[chain_of_thought, field],
                    verbose=self.verbose,
                    **self.model_args
                )
                eval_results_str = json.dumps(eval_result[0], indent=2)
                logger.info(f"Revision {revision_idx + 1}: `{field.name}`")
                revised = revisor(**inputs, evaluation_result=eval_results_str)
                self.tokens += revisor.tokens
                if revised[field.name].strip():
                    inputs[field.name] = revised[field.name].strip()

            if finished:
                break

        return inputs
