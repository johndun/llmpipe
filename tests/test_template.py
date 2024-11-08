import pytest
from llmpipe.template import Template


def test_basic_template_substitution():
    """Test basic key substitution works."""
    template = Template("Hello {{name}}!")
    result = template.format(name="World")
    assert result == "Hello World!"


def test_multiple_substitutions():
    """Test multiple key substitutions work."""
    template = Template("{{greeting}} {{name}}! How is {{location}}?")
    result = template.format(greeting="Hello", name="Alice", location="London")
    assert result == "Hello Alice! How is London?"


def test_missing_key_unchanged():
    """Test that missing keys are left unchanged in template."""
    template = Template("Hello {{name}}! How is {{location}}?")
    result = template.format(name="Bob")
    assert result == "Hello Bob! How is {{location}}?"


def test_empty_value_substitution():
    """Test that empty values are handled correctly."""
    template = Template("Name: {{name}}, Title: {{title}}")
    result = template.format(name="", title="Dr")
    assert result == "Name: , Title: Dr"


def test_non_string_value_conversion():
    """Test that non-string values are converted to strings."""
    template = Template("Count: {{number}}, Active: {{boolean}}")
    result = template.format(number=42, boolean=True)
    assert result == "Count: 42, Active: True"


def test_template_unchanged():
    """Test that the original template string is not modified."""
    template = Template("Hello {{name}}!")
    template.format(name="World")
    assert template.template == "Hello {{name}}!"
