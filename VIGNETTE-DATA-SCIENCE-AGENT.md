# Vignette: Data analysis script generation

A project requires a path (to store scripts and artifacts) and a dataset:

```bash
python -m llmpipe.data_science_agent.initialize_project \
    --repo-path ~/test_repo \
    --data-path ~/data/dat.jsonl \
    --verbose
```

This generates an empty repo and adds several files:

- sample_data.md: 3 random records from the dataset
- data_schema: LLM generated data schema (based on sample.md)
- cli_script_template.py, data_io_template.py: Scripts illustrating implementation patterns
- univariate_summaries_task.yaml: A yaml file containing task and script_name fields

Write an analysis script, run it, fix bugs, summarize the results.

```bash
python -m llmpipe.data_science_agent.write_script \
    --repo-path ~/test_repo \
    --data-path ~/data/dat.jsonl \
    --task "Generate a subsampled version of the dataset named dat_small.jsonl with n=100 random samples to use for testing scripts" \
    --max-revisions 2 \
    --verbose

python -m llmpipe.data_science_agent.write_script \
    --repo-path ~/test_repo \
    --data-path ~/data/dat_small.jsonl \
    --task "Fit an initial baseline fine tuned ROBERTA model to predict the labels with the text field." \
    --max-revisions 2 \
    --verbose
```

Generate a follow up based on reading the data analysis summaries in the repo:

```bash
python -m llmpipe.data_science_agent.generate_followup \
    --repo-path ~/test_repo \
    --data-path ~/data/dat.jsonl \
    --max-revisions 2 \
    --verbose
```
