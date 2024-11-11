Module llmpipe.llmprompt_formany
================================

Classes
-------

`LlmPromptForMany(model: str = 'anthropic/claude-3-5-sonnet-20241022', system_prompt: str = '', max_tokens: int = 4096, top_p: float = 1.0, temperature: float = 0.0, tools: List[Callable] = None, max_tool_calls: int = 6, stream: bool = False, inputs: List[llmpipe.field.Input] = <factory>, output: llmpipe.field.Output = None, inputs_header: str = 'You are provided the following inputs:', task: str = '', details: str = '', footer: str = None, cot_string: str = 'Begin by thinking step by step')`
:   An LLM prompt class that returns a list of outputs

    ### Ancestors (in MRO)

    * llmpipe.llmchat.LlmChat

    ### Class variables

    `cot_string: str`
    :

    `details: str`
    :   Task details that come after the input output definition sections

    `footer: str`
    :   An optional prompt footer (text for the very end of the prompt)

    `inputs: List[llmpipe.field.Input]`
    :   Prompt inputs

    `inputs_header: str`
    :   The inputs definition section header

    `output: llmpipe.field.Output`
    :   The output

    `task: str`
    :   The task description at the top of the prompt

    ### Instance variables

    `prompt: str`
    :   Returns a prompt for generating the output

    ### Methods

    `discard(self, **inputs: List[Dict]) ‑> List[Dict]`
    :

    `evaluate(self, break_after_first_fail: bool = False, **inputs) ‑> List[Dict]`
    :

    `revise(self, max_revisions: int = 6, **inputs) ‑> List[Dict]`
    :

    `verify_outputs(self, outputs)`
    :