import pytest
from llmpipe.prompt_module import PromptModule
from llmpipe.field import Input, Output


def test_promptmodule_init():
    """Test basic PromptModule initialization"""
    prompt = PromptModule()
    assert prompt.inputs == []
    assert prompt.outputs == []
    assert prompt.task == ""
    assert prompt.details == ""
    assert isinstance(prompt.inputs_header, str)


def test_promptmodule_with_fields():
    """Test PromptModule with input and output fields"""
    input_field = Input(name="color", description="A color name")
    output_field = Output(name="mood", description="The mood this color evokes")
    
    prompt = PromptModule(
        inputs=[input_field],
        outputs=[output_field],
        task="Determine the mood associated with a color"
    )
    
    assert len(prompt.inputs) == 1
    assert len(prompt.outputs) == 1
    assert prompt.task == "Determine the mood associated with a color"


def test_prompt_template():
    """Test prompt template generation"""
    input_field = Input(name="number", description="A number to analyze")
    output_field = Output(name="analysis", description="Analysis of the number")
    
    prompt = PromptModule(
        inputs=[input_field],
        outputs=[output_field],
        task="Analyze the given number"
    )
    
    template = prompt.prompt
    assert "# Task Description" in template
    assert "Analyze the given number" in template
    assert "number" in template
    assert "analysis" in template


def test_verify_outputs():
    """Test output verification"""
    output_field = Output(name="result", description="The result")
    prompt = PromptModule(outputs=[output_field])
    
    # Should pass
    prompt.verify_outputs({"result": "test"})
    
    # Should fail
    with pytest.raises(AssertionError):
        prompt.verify_outputs({"wrong_field": "test"})


def test_promptmodule_call():
    """Test PromptModule call with mocked response"""
    class MockPromptModule(PromptModule):
        def _call(self, prompt="", prefill="", tool_call_depth=0):
            return "<result>42</result>"

    output_field = Output(name="result", description="The result")
    prompt = MockPromptModule(outputs=[output_field])
    
    result = prompt()
    assert result == {"result": "42"}
