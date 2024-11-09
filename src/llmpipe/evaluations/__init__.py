from typing import List, Union

from .core import Evaluation


def eval_factory(
        type: str,
        field: str,
        value: Union[int, float, str, List] = None,
        label: str = None,
        **kwargs
) -> Evaluation:
    """Returns an evaluation

    Args:
        type (str): The type of evaluation to create
        field (str): The field that the evaluation applies to
        value (Union[int, float, str]): Initialization parameter to pass to the Evaluation subclass
        label (str): A brief description of the requirement
        **kwargs: Keyword arguments passed to `LlmEvaluation`

    Returns:
        Evaluation: An initalized evaluation

    """
    from llmpipe.evaluations.max_chars import MaxCharacters
    from llmpipe.evaluations.no_blocked_terms import NoBlockedTerms
    from llmpipe.evaluations.no_long_words import NoLongWords
    from llmpipe.evaluations.no_slashes import NoSlashes
    from llmpipe.evaluations.no_square_brackets import NoSquareBrackets
    from llmpipe.evaluations.not_in_blocked_list import NotInBlockedList
    from llmpipe.evaluations.is_in_allow_list import IsInAllowList
    from llmpipe.evaluations.llm_eval import LlmEvaluation

    if type == "max_chars":
        return MaxCharacters(field=field, max_chars=value, requirement=label)

    if type == "no_square_brackets":
        return NoSlashes(field=field, requirement=label)

    if type == "no_slashes":
        return NoSquareBrackets(field=field, requirement=label)

    if type in("not_contains", "no_blocked_terms"):
        return NoBlockedTerms(field=field, blocked_terms=value, requirement=label)

    if type == "not_in_blocked_list":
        return NotInBlockedList(field=field, blocked_list=value, requirement=label)

    if type == "not_contains_field":
        return NoBlockedTerms(field=field, blocked_terms_field=value, requirement=label)

    if type == "not_in_blocked_list_field":
        return NotInBlockedList(field=field, blocked_list_field=value, requirement=label)

    if type == "no_long_words":
        return NoLongWords(field=field, max_chars=value, requirement=label)

    if type in("is_in", "is_in_allow_list"):
        return IsInAllowList(field=field, allowed_terms=value, requirement=label)

    if type == "is_in_field":
        return IsInAllowList(field=field, allowed_terms_field=value, requirement=label)

    if type == "llm":
        return LlmEvaluation(field=field, requirement=value, **kwargs)

    raise NotImplementedError
