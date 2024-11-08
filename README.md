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

To build the docs:

```bash
pdoc -o docs --force src/llmpipe
```

To clean notebooks before committing:

```bash
nb-clean clean -o notebooks/*.ipynb
```