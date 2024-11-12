Module llmpipe.modules.document_chunker
=======================================

Classes
-------

`DocumentChunker(**kwargs)`
:   Break a document into sections and subsections.
    
    - If the first subsection of the document contains only the title, it will have equal metadata keys: document == section == subsection
    - If a subsection contains only a section header, it will have equal metadata keys: section == subsection
    
    Initialization Parameters:
        **kwargs: Keyword arguments passed to `LlmPrompt`
    
    Args:
        document: The document to chunk
        document_title: An optional title for the document. One will be generated if not provided.
    
    Returns:
        A list of dictionaries with keys: document, section, subsection, content