Module llmpipe.evaluations
==========================

Sub-modules
-----------
* llmpipe.evaluations.core
* llmpipe.evaluations.is_in_allow_list
* llmpipe.evaluations.is_in_string
* llmpipe.evaluations.llm_eval
* llmpipe.evaluations.max_chars
* llmpipe.evaluations.no_blocked_terms
* llmpipe.evaluations.no_long_words
* llmpipe.evaluations.no_slashes
* llmpipe.evaluations.no_square_brackets
* llmpipe.evaluations.not_in_blocked_list

Functions
---------

`eval_factory(type: str, field: str, value: Union[int, float, str, List] = None, label: str = None, **kwargs) ‑> llmpipe.evaluations.core.Evaluation`
:   Returns an evaluation
    
    Args:
        type (str): The type of evaluation to create
        field (str): The field that the evaluation applies to
        value (Union[int, float, str]): Initialization parameter to pass to the Evaluation subclass
        label (str): A brief description of the requirement
        **kwargs: Keyword arguments passed to `LlmEvaluation`
    
    Returns:
        Evaluation: An initalized evaluation