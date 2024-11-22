Module llmpipe.evaluations.llm_eval
===================================

Classes
-------

`LlmEvaluation(field: str, requirement: str, type: str = 'llm', use_cot: bool = True, inputs: List[llmpipe.field.Input] = <factory>, field_description: str = '')`
:   An LLM-as-a-judge evaluation

    ### Ancestors (in MRO)

    * llmpipe.evaluations.core.Evaluation

    ### Class variables

    `field_description: str`
    :   Description of the field to apply the evaluation to

    `inputs: List[llmpipe.field.Input]`
    :   Inputs needed to perform the evaluation

    `use_cot: bool`
    :   If true, add a chain-of-thought request

    ### Instance variables

    `tokens`
    :