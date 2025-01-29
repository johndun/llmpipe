# llmpipe
A toolkit for building LLM pipelines

## Setup

First, create a python environment using `venv`. Requires python >= 3.10. Check this with:

```bash
python3 -m venv llmpipe
source llmpipe/bin/activate
```

From the cloned repo:

```bash
pip install "."
# or
pip install -e ".[dev]"
```

## Notes

Models:

- deepseek/deepseek-reasoner
- claude-3-5-haiku-20241022
- claude-3-5-sonnet-20241022

To build the docs:

```bash
pdoc -o docs --force src/llmpipe
```

To clean notebooks before committing:

```bash
nb-clean clean -o notebooks/*.ipynb
```

Basic prompting
```bash
python -m llmpipe.llmchat \
    --model deepseek/deepseek-reasoner \
    --stream \
    --temperature 1.3 \
     experiments/prompt.md


python -m llmpipe.modules.address_comments \
    --model deepseek/deepseek-reasoner \
    --verbose \
    --temperature 1.3 \
    --file-out experiments/doc2.md \
    experiments/doc.md
```

Document editing
```bash
python -m llmpipe.modules.address_comments --help
python -m llmpipe.modules.address_comments \
    --model deepseek/deepseek-reasoner \
    --verbose \
    --temperature 1.3 \
    --file-out experiments/doc2.md \
    experiments/doc.md
```


## Aider

### Deepseek

```bash
aider --model deepseek/deepseek-reasoner --no-analytics --read src/llmpipe/prompt_module.py src/llmpipe/llmchat.py
```

Update llmchat.py to include a cli entrypoint function like `run_yaml_prompt`. Include a arg `prompt_path` which should loaded as a string and treated as a LlmChat prompt.

```bash
python -m llmpipe.llmchat --help
python -m llmpipe.llmchat --verbose --model claude-3-5-haiku-20241022 experiments/test_prompt.md  > experiments/test_prompt_response.md 2>&1
```

