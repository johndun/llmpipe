Module llmpipe.xml
==================

Functions
---------

`parse_text_for_one_tag(text: str, tag: str) ‑> str`
:   Extracts the (last) text contained in the specified XML/HTML tag.
    
    Args:
        text (str): A string with XML tags
        tag (str): The tag, without angle braces, to extract
    
    Returns:
        List[str]: A list of strings, each representing the content inside a tag block

`parse_text_for_tag(text: str, tag: str) ‑> List[str]`
:   Extracts the text within all the outermost specified XML/HTML tag.
    
    Args:
        text (str): A string with XML tags
        tag (str): The tag, without angle braces, to extract
    
    Returns:
        List[str]: A list of strings, each representing the content inside a tag block

`parse_text_for_tags(text: str) ‑> List[llmpipe.xml.XmlBlock]`
:   Extracts the text within all the outermost XML/HTML tags.
    
    Args:
        text (str): A string with XML tags
    
    Returns:
        List[XmlBlock]: A list of XmlBlock objects, each containing the tag name and the content inside the tag block

Classes
-------

`XmlBlock(tag: str, content: str)`
:   XmlBlock(tag: str, content: str)

    ### Class variables

    `content: str`
    :

    `tag: str`
    :