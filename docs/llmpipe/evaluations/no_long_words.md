Module llmpipe.evaluations.no_long_words
========================================

Classes
-------

`NoLongWords(field: str, requirement: str = None, type: str = 'deterministic', max_chars: int = 10)`
:   Evaluates that a field has no words with more than `max_chars` characters
    
    Usage:
    
    ```python
    no_long_words = NoLongWords(field="text", max_chars=9)
    print(no_long_words(text="A vegetarian nightingale"))
    print(no_long_words(text="cat dog"))
    ```

    ### Ancestors (in MRO)

    * llmpipe.evaluations.core.Evaluation

    ### Class variables

    `max_chars: int`
    :