Module llmpipe.evaluations.not_in_blocked_list
==============================================

Classes
-------

`NotInBlockedList(field: str, requirement: str = None, type: str = 'deterministic', blocked_list: List[str] = None, blocked_list_field: str = None)`
:   Ensure that a field is not in a blocked list
    
    Usage:
    
    ```python
    blocked_list1 = NotInBlockedList(field="color", blocked_list=["green"])
    print(blocked_list1(color="black"))
    print(blocked_list1(color="green"))
    
    blocked_list2 = NotInBlockedList(field="color", blocked_list_field="bad_colors")
    print(blocked_list2(color="black", bad_colors=["green"]))
    print(blocked_list2(color="green", bad_colors=["green"]))
    ```

    ### Ancestors (in MRO)

    * llmpipe.evaluations.core.Evaluation

    ### Class variables

    `blocked_list: List[str]`
    :

    `blocked_list_field: str`
    :