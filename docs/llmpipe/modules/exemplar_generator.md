Module llmpipe.modules.exemplar_generator
=========================================

Classes
-------

`ExemplarGenerator(input: llmpipe.field.Input, n: int = 5, **kwargs)`
:   Returns a list of dictionaries containing passing/failing exemplars.
    
    - Inputs for the requirement are defined at class initialization
    - The evaluation is passed when the instance is called
    
    Initialization Parameters:
        input (Input): An `Input` for the evaluation.
        **kwargs: Keyword arguments passed to `LlmPrompt`
    
    Args:
        **inputs: Values for the inputs defined in `self.inputs`
    
    Returns:
        A list of dictionaries with additional keys: requirement, groundtruth