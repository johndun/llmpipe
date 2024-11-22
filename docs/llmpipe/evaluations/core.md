Module llmpipe.evaluations.core
===============================

Classes
-------

`EvalResult(field: str, requirement: str, evaluation_result: str, reason: str = '')`
:   An evaluation result

    ### Class variables

    `evaluation_result: str`
    :   The evaluation result, e.g., 'PASS' or 'FAIL'

    `field: str`
    :   The field that the evaluation applies to

    `reason: str`
    :   An optional reason for the evaluation

    `requirement: str`
    :   A brief description of the requirement

`Evaluation(field: str, requirement: str, type: str)`
:   A single field evaluation

    ### Descendants

    * llmpipe.evaluations.contains_all.ContainsAll
    * llmpipe.evaluations.contains_one.ContainsOne
    * llmpipe.evaluations.contains_xml.ContainsXml
    * llmpipe.evaluations.is_in_allow_list.IsInAllowList
    * llmpipe.evaluations.is_in_string.IsInString
    * llmpipe.evaluations.llm_eval.LlmEvaluation
    * llmpipe.evaluations.max_chars.MaxCharacters
    * llmpipe.evaluations.max_words.MaxWords
    * llmpipe.evaluations.no_blocked_terms.NoBlockedTerms
    * llmpipe.evaluations.no_long_words.NoLongWords
    * llmpipe.evaluations.no_slashes.NoSlashes
    * llmpipe.evaluations.no_square_brackets.NoSquareBrackets
    * llmpipe.evaluations.not_in_blocked_list.NotInBlockedList

    ### Class variables

    `field: str`
    :   The field that the evaluation applies to

    `requirement: str`
    :   A brief description of the requirement

    `type: str`
    :   The evaluation type, e.g., 'deterministic' or 'llm'