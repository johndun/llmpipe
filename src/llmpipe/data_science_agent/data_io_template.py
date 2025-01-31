# Use read_data and write_data from llmpipe for CSV, tab-delimited, and jsonlines data io
from llmpipe import read_data, write_data
samples = read_data(data_path)  # Infers file type; returns a list of dicts

# write_data takes a list of dicts and a path
write_data(samples, "path/to/output.jsonl")  # or csv or txt
