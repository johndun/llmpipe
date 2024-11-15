import pytest
from llmpipe.chunk_text import chunk_text

def test_basic_chunking():
    """Test basic text chunking with simple paragraphs"""
    text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."
    chunks = chunk_text(text, 5)
    assert len(chunks) == 2
    assert "This is paragraph one." in chunks[0]
    assert "This is paragraph two." in chunks[0]
    assert "This is paragraph three." in chunks[1]

def test_large_paragraph_splitting():
    """Test splitting of large paragraphs"""
    text = "This is a very long paragraph that should be split into multiple chunks because it exceeds the word limit that we have set for testing purposes."
    chunks = chunk_text(text, 5)
    assert len(chunks) == 4
    assert all(len(chunk.split()) <= 5 for chunk in chunks)

def test_sentence_boundary_splitting():
    """Test splitting at sentence boundaries when possible"""
    text = "First sentence. Second sentence. Third sentence. Fourth sentence."
    chunks = chunk_text(text, 4)
    assert len(chunks) == 2
    assert "First sentence. Second sentence." in chunks[0]
    assert "Third sentence. Fourth sentence." in chunks[1]

def test_empty_input():
    """Test handling of empty input"""
    assert chunk_text("", 10) == []
    assert chunk_text("\n\n\n", 10) == []

def test_single_word_chunks():
    """Test with very small chunk size"""
    text = "One two three."
    chunks = chunk_text(text, 1)
    assert len(chunks) == 3
    assert chunks[0] == "One"
    assert chunks[1] == "two"
    assert chunks[2] == "three."

def test_multiple_newlines():
    """Test handling of multiple newlines"""
    text = "Para one.\n\n\nPara two.\n\nPara three."
    chunks = chunk_text(text, 4)
    assert len(chunks) == 2
    assert "Para one." in chunks[0]
    assert "Para two." in chunks[0]
    assert "Para three." in chunks[1]

def test_exact_chunk_size():
    """Test chunks that exactly match the word limit"""
    text = "One two three.\n\nFour five six.\n\nSeven eight nine."
    chunks = chunk_text(text, 3)
    assert len(chunks) == 3
    assert chunks[0] == "One two three."
    assert chunks[1] == "Four five six."
    assert chunks[2] == "Seven eight nine."
