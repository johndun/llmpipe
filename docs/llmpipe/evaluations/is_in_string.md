Module llmpipe.evaluations.is_in_string
=======================================

Classes
-------

`IsInString(field: str, requirement: str = None, type: str = 'deterministic', target_string: str = None, target_string_field: str = None)`
:   Ensure that a field is contained within a target string
    
    Usage:
    
    ```python
    # Using direct string
    in_string1 = IsInString(field="word", target_string="The quick brown fox")
    print(in_string1(word="quick"))  # PASS
    print(in_string1(word="slow"))   # FAIL
    
    # Using field reference
    in_string2 = IsInString(field="word", target_string_field="text")
    print(in_string2(word="dog", text="The dog barks"))  # PASS
    print(in_string2(word="cat", text="The dog barks"))  # FAIL
    ```

    ### Ancestors (in MRO)

    * llmpipe.evaluations.core.Evaluation

    ### Class variables

    `target_string: str`
    :

    `target_string_field: str`
    :