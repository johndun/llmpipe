# Vignette: Data analysis script generation

A project requires a path (to store scripts and artifacts) and a dataset:

```bash
python -m llmpipe.data_science_agent.initialize_project \
    --repo-path ~/test_repo \
    --data-path ~/Work/llmpipe/resources/dummy_data.jsonl \
    --verbose
```

This generates an empty repo and adds 2 files, one with 3 random records from the dataset and one with an LLM generated data schema (based on these 3 records).

Generate and execute a data analysis script, and generate a summary.

```bash
python -m llmpipe.data_science_agent.generate_eda_script \
    --repo-path ~/test_repo \
    --data-path ~/Work/llmpipe/resources/dummy_data.jsonl \
    --task "Generate univariate summary statistics. Include missing value counts. Include distinct value counts. Include a table of frequency counts for fields with fewer than 20 distinct values." \
    --max-revisions 3 \
    --verbose
```

Generate a follow up based on reading the data analysis summaries in the repo:

```bash
python -m llmpipe.data_science_agent.generate_followup \
    --repo-path ~/test_repo \
    --data-path ~/Work/llmpipe/resources/dummy_data.jsonl \
    --max-revisions 3 \
    --verbose
```
