Module llmpipe.llmprompt
========================

Classes
-------

`LlmPrompt(model: str = 'anthropic/claude-3-5-sonnet-20241022', system_prompt: str = '', max_tokens: int = 4096, top_p: float = 1.0, temperature: float = 0.0, tools: List[Callable] = None, max_tool_calls: int = 6, stream: bool = False, inputs: List[llmpipe.field.Input] = <factory>, outputs: List[llmpipe.field.Output] = <factory>, inputs_header: str = 'You are provided the following inputs:', task: str = '', details: str = '', footer: str = None, break_after_first_fail: bool = True)`
:   An LLM prompt class
    
    - Constructions a prompt template using the input and output fields.
    - Any Evaluations associated with the outputs will be executed. Non-passing evaluations will be returned.
    - Non-llm evals will be run first.

    ### Ancestors (in MRO)

    * llmpipe.llmchat.LlmChat

    ### Class variables

    `break_after_first_fail: bool`
    :   If true, returns only the 1st failed evaluation

    `details: str`
    :   Task details that come after the input output definition sections

    `footer: str`
    :   An optional prompt footer (text for the very end of the prompt)

    `inputs: List[llmpipe.field.Input]`
    :   Prompt inputs

    `inputs_header: str`
    :   The inputs definition section header

    `outputs: List[llmpipe.field.Output]`
    :   Prompt outputs

    `task: str`
    :   The task description at the top of the prompt

    ### Instance variables

    `prompt: str`
    :   Returns a prompt for generating the output

    ### Methods

    `evaluate(self, **inputs) ‑> Dict`
    :   Run evaluations

    `revise(self, max_revisions: int = 6, **inputs) ‑> Dict`
    :   Evaluate and revise

    `verify_outputs(self, outputs)`
    :