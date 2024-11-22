Module llmpipe.chunk_text
=========================

Functions
---------

`chunk_text(text, n_words_per_chunk)`
:   Splits text into chunks by adding paragraphs until reaching `n_words_per_chunk`.
    If a paragraph is larger than the chunk size, it will be split at the nearest
    sentence boundary or, if necessary, at the word boundary.
    
    :param text: Text to split into chunks
    :param n_words_per_chunk: Approximate number of words per chunk.
    :return: A list of text chunks.