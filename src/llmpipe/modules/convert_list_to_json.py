import json
from typing import List, Dict

from llmpipe.field import Input, Output
from llmpipe.llmprompt import LlmPrompt


class ConvertListToJson:
    """Convert a markdown list to a JSON formatted list

    Initialization Parameters:
        **kwargs: Keyword arguments passed to `LlmPrompt`

    Args:
        text_list: A text/markdown list

    Returns:
        A list of strings
    """
    def __init__(self, **kwargs):
        inputs = Input("text_list", "Text containing a list")
        json_list = Output(
            "json_list", "JSON formatted version of the list from `text_list`",
            inputs=[inputs],
            evaluations=[
                {"type": "llm", "value": "Each element of the generated list should exactly match a single top-level item in the original list, including newlines and nested items, but not including the leading bullet or list index"}
            ]
        )
        self.converter = LlmPrompt(
            task="""Convert the list found in `text_list` to a JSON-formatted list: ["item 1", "item 2", ...].""",
            inputs=json_list.inputs,
            outputs=[json_list],
            **kwargs
        )

    def __call__(self, text_list: str) -> List[str]:
        results = self.converter(text_list=text_list)
        revised_results = self.converter.revise(text_list=text_list, **results)
        return json.loads(revised_results["json_list"])
