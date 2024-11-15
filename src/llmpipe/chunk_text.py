from dataclasses import dataclass
from typing import List, Tuple


def chunk_text(text, n_words_per_chunk):
    """
    Splits text into chunks by adding paragraphs until reaching `n_words_per_chunk`.
    If a paragraph is larger than the chunk size, it will be split at the nearest
    sentence boundary or, if necessary, at the word boundary.

    :param text: Text to split into chunks
    :param n_words_per_chunk: Approximate number of words per chunk.
    :return: A list of text chunks.
    """
    # Split the text into paragraphs
    paragraphs = [x for x in text.split('\n') if x]

    # Initialize variables
    chunks = []
    current_chunk = []
    current_word_count = 0

    def split_large_paragraph(paragraph, max_words):
        """Helper function to split a large paragraph into smaller chunks."""
        words = paragraph.split()
        if len(words) <= max_words:
            return [paragraph]

        # Try to split at sentence boundaries first
        sentences = []
        current_sentence = []

        for word in words:
            current_sentence.append(word)
            # Check for sentence endings (., !, ?)
            if word.endswith(('.', '!', '?')):
                sentences.append(' '.join(current_sentence))
                current_sentence = []

        # Add any remaining words as the last sentence
        if current_sentence:
            sentences.append(' '.join(current_sentence))

        # Now chunk the sentences
        paragraph_chunks = []
        current_para_chunk = []
        current_para_word_count = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())

            # If a single sentence is too long, split it at word boundaries
            if sentence_words > max_words:
                sentence_words_list = sentence.split()
                while sentence_words_list:
                    chunk_words = sentence_words_list[:max_words]
                    paragraph_chunks.append(' '.join(chunk_words))
                    sentence_words_list = sentence_words_list[max_words:]
                continue

            # If adding this sentence would exceed the limit
            if current_para_word_count + sentence_words > max_words:
                # Store the current chunk and start a new one
                if current_para_chunk:
                    paragraph_chunks.append(' '.join(current_para_chunk))
                current_para_chunk = [sentence]
                current_para_word_count = sentence_words
            else:
                current_para_chunk.append(sentence)
                current_para_word_count += sentence_words

        # Add the last chunk if any
        if current_para_chunk:
            paragraph_chunks.append(' '.join(current_para_chunk))

        return paragraph_chunks

    for paragraph in paragraphs:
        # Count words in the paragraph
        word_count = len(paragraph.split())

        # If the paragraph is larger than the chunk size, split it
        if word_count > n_words_per_chunk:
            # First, add any accumulated chunks
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_word_count = 0

            # Split and add the large paragraph
            paragraph_chunks = split_large_paragraph(paragraph, n_words_per_chunk)
            chunks.extend(paragraph_chunks)
            continue

        # If adding this paragraph exceeds the word limit
        if current_word_count + word_count > n_words_per_chunk:
            # Add the current chunk to the list of chunks
            chunks.append('\n\n'.join(current_chunk))
            # Reset the current chunk and word count
            current_chunk = []
            current_word_count = 0

        # Add the paragraph to the current chunk
        current_chunk.append(paragraph)
        current_word_count += word_count

    # Add the last chunk if any
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks
