Module llmpipe.evaluations
==========================

Sub-modules
-----------
* llmpipe.evaluations.core
* llmpipe.evaluations.is_in_allow_list
* llmpipe.evaluations.max_chars
* llmpipe.evaluations.no_blocked_terms
* llmpipe.evaluations.no_long_words
* llmpipe.evaluations.no_slashes
* llmpipe.evaluations.no_square_brackets
* llmpipe.evaluations.not_in_blocked_list

Functions
---------

`deterministic_eval_factory(field: str, value: Union[int, float, str] = None, label: str = None) ‑> llmpipe.evaluations.core.Evaluation`
:   Returns an evaluation
    
    Args:
        field (str): The field that the evaluation applies to
        value (Union[int, float, str]): Initialization parameter to pass to the Evaluation subclass
        label (str): A brief description of the requirement
    
    Returns:
        Evaluation: An initalized evaluation