Module llmpipe.field
====================

Classes
-------

`Input(name: str, description: str = '')`
:   Defines an LLM module input or output

    ### Descendants

    * llmpipe.field.Output

    ### Class variables

    `description: str`
    :   Description for the field

    `name: str`
    :   A name for the field

    ### Instance variables

    `definition: str`
    :   Return a formatted definition string

    `input_template: str`
    :   Returns an input template using xml tags and double curly braces

    `markdown: str`
    :   Apply markdown formatting to the input name

    `xml: str`
    :   Apply xml formatting to the input name

    `xml_close: str`
    :   Apply xml formatting to the input name

`Output(name: str, description: str = '', evaluations: List[llmpipe.evaluations.core.Evaluation] = <factory>, inputs: List[llmpipe.field.Input] = <factory>)`
:   Defines an LLM module input or output with evaluations and linked inputs

    ### Ancestors (in MRO)

    * llmpipe.field.Input

    ### Class variables

    `evaluations: List[llmpipe.evaluations.core.Evaluation]`
    :   Field evaluations

    `inputs: List[llmpipe.field.Input]`
    :   Inputs needed to generate this field