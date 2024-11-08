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

    * llmpipe.evaluations.max_chars.MaxCharacters

    ### Class variables

    `field: str`
    :   The field that the evaluation applies to

    `requirement: str`
    :   A brief description of the requirement

    `type: str`
    :   The evaluation type, e.g., 'deterministic' or 'llm'