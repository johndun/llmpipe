from llmpipe.field import Input, Output
from llmpipe.evaluations.max_chars import MaxCharacters


def test_field_basic():
    """Test basic Field initialization"""
    field = Output(name="test", description="A test field")
    assert field.name == "test"
    assert field.description == "A test field"
    assert field.evaluations == []
    assert field.inputs == []


def test_field_with_evaluations():
    """Test Field with evaluations"""
    field = Output(
        name="test",
        description="A test field",
        evaluations=[{"type": "max_chars", "value": 10}]
    )
    assert len(field.evaluations) == 1
    assert isinstance(field.evaluations[0], MaxCharacters)
    assert field.evaluations[0].max_chars == 10


def test_field_with_inputs():
    """Test Field with nested inputs"""
    nested_input = {
        "name": "nested",
        "description": "A nested field"
    }
    field = Output(
        name="test",
        description="A test field",
        inputs=[nested_input]
    )
    assert len(field.inputs) == 1
    assert isinstance(field.inputs[0], Input)
    assert field.inputs[0].name == "nested"


def test_field_markdown():
    """Test markdown property"""
    field = Output(name="test", description="A test field")
    assert field.markdown == "`test`"


def test_field_xml():
    """Test xml and xml_close properties"""
    field = Output(name="test", description="A test field")
    assert field.xml == "<test>"
    assert field.xml_close == "</test>"


def test_field_definition():
    """Test definition property"""
    field = Output(name="test", description="A test field")
    assert field.definition == "<test>\nA test field\n</test>"


def test_field_input_template():
    """Test input_template property"""
    field = Output(name="test", description="A test field")
    expected = "<test>\n{{test}}\n</test>"
    assert field.input_template == expected
