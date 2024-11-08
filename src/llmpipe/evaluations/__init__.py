from typing import Union

from .core import Evaluation
from .max_chars import MaxCharacters
from .no_blocked_terms import NoBlockedTerms
from .no_long_words import NoLongWords
from .no_slashes import NoSlashes
from .no_square_brackets import NoSquareBrackets
from .not_in_blocked_list import NotInBlockedList
from .is_in_allow_list import IsInAllowList


def deterministic_eval_factory(
        type: str,
        field: str,
        value: Union[int, float, str] = None,
        label: str = None
) -> Evaluation:
    """Returns an evaluation

    Args:
        type s(str): The type of evaluation to create
        field (str): The field that the evaluation applies to
        value (Union[int, float, str]): Initialization parameter to pass to the Evaluation subclass
        label (str): A brief description of the requirement

    Returns:
        Evaluation: An initalized evaluation

    """
    if type == "max_chars":
        return MaxCharacters(field=field, max_chars=value, requirement=label)

    if type == "no_square_brackets":
        return NoSlashes(field=field, requirement=label)

    if type == "no_slashes":
        return NoSquareBrackets(field=field, requirement=label)

    if type == "not_contains":
        return NoBlockedTerms(field=field, blocked_terms=value, requirement=label)

    if type == "not_in_blocked_list":
        return NotInBlockedList(field=field, blocked_list=value, requirement=label)

    if type == "not_contains_field":
        return NoBlockedTerms(field=field, blocked_terms_field=value, requirement=label)

    if type == "not_in_blocked_list_field":
        return NotInBlockedList(field=field, blocked_list_field=value, requirement=label)

    if type == "no_long_words":
        return NoLongWords(field=field, max_chars=value, requirement=label)

    if type == "is_in":
        return IsInAllowList(field=field, allowed_terms=value, requirement=label)

    if type == "is_in_field":
        return IsInAllowList(field=field, allowed_terms_field=value, requirement=label)

    raise NotImplementedError
