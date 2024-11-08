Module llmpipe.field
====================

Classes
-------

`Field(name: str, description: str, evaluations: List[llmpipe.evaluations.core.Evaluation] = <factory>, inputs: List[ForwardRef('Field')] = <factory>)`
:   Defines an LLM module input or output

    ### Class variables

    `description: str`
    :   Description for the field

    `evaluations: List[llmpipe.evaluations.core.Evaluation]`
    :   Field evaluations

    `inputs: List[llmpipe.field.Field]`
    :   Inputs needed to generate this field

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