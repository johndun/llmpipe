import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict

from datasets import Dataset

from llmpipe.field import Input, Output
from llmpipe.llmchat import LlmChat
from llmpipe.template import Template
from llmpipe.xml_utils import parse_text_for_one_tag
from llmpipe.prompt_module import PromptModule


logger = logging.getLogger(__name__)


@dataclass
class RevisorModule(PromptModule):
    """An LLM prompt class"""
    task: str = "Revise an output"

    def __call__(self, num_proc: int = 1, **inputs) -> Dict:
        if not isinstance(list(inputs.values())[0], list):
            return self.revise(**inputs)

        return (
            Dataset.from_dict(inputs)
            .map(
                lambda sample: sample | self.revise(**sample),
                num_proc=num_proc,
                batched=False
            )
        ).to_dict()

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
                revisor = PromptModule(
                    task="Your task is to generate an updated version of the field indicated in the evaluation result so that it meets all evaluation criteria and requirements.",
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