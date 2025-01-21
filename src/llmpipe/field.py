from dataclasses import dataclass, field, asdict
from typing import List, Union, Dict
from io import StringIO

from llmpipe.evaluations import eval_factory, Evaluation


@dataclass
class Input:
    """Defines an LLM module input or output"""
    name: str  #: A name for the field
    description: str = ""  #: Description for the field

    @property
    def markdown(self) -> str:
        """Apply markdown formatting to the input name"""
        return f"`{self.name}`"

    @property
    def xml(self) -> str:
        """Apply xml formatting to the input name"""
        return f"<{self.name}>"

    @property
    def xml_close(self) -> str:
        """Apply xml formatting to the input name"""
        return f"</{self.name}>"

    @property
    def definition(self) -> str:
        """Return a formatted definition string"""
        return f"{self.xml}\n{self.description}\n{self.xml_close}"

    @property
    def input_template(self) -> str:
        """Returns an input template using xml tags and double curly braces"""
        return self.xml + "\n{{" + self.name + "}}\n" + self.xml_close


@dataclass
class Output(Input):
    """Defines an LLM module input or output with evaluations and linked inputs

    Evaluations can be dictionaries with keys:

        type (str): The type of evaluation to create
        value (Union[int, float, str]): Initialization parameter to pass to the Evaluation subclass
        label (str): A brief description of the requirement
        **kwargs: Keyword arguments passed to `LlmEvaluation`
    
    """
    evaluations: List[Union[Dict, Evaluation]] = field(default_factory=lambda: [])  #: Field evaluations
    inputs: List[Input] = field(default_factory=lambda: [])  #: Inputs needed to evaluate this field(!!)

    def __post_init__(self):
        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

        # Convert any dict evaluations to Evaluation objects
        self.evaluations = [
            eval_factory(
                field=self.name,
                field_description=self.description,
                inputs=x["inputs"] if "inputs" in x else self.inputs,
                **{k: v for k, v in x.items() if k != "inputs"}
            ) if isinstance(x, dict) else x
            for x in self.evaluations
        ]

    @property
    def definition(self) -> str:
        """Return a formatted definition string"""
        txt = [self.xml, self.description]
        evals = [x for x in self.evaluations if not x.hidden]
        if evals:
            txt.append(f"\nRequirements:")
            txt.append("\n".join([f"- {evl.requirement}" for evl in evals]))
        txt.append(self.xml_close)
        return "\n".join(txt)

    def process(self, x):
        return x


@dataclass
class JsonOutput(Output):
    def process(self, x):
        return json.loads(x)


def parse_tsv_string(tsv_string, as_columns=True):
    """
    Parse a tab-separated string with header and return data in either columnar or row-based format.
    
    Args:
        tsv_string (str): String containing TSV data
        as_columns (bool): If True, return dict of lists (columnar format)
                         If False, return list of dicts (row format)
        
    Returns:
        Union[dict, list]: Either:
            - dict mapping column names to lists of values (if as_columns=True)
            - list of dictionaries, each representing a row (if as_columns=False)
    """
    import csv
    from io import StringIO
    from collections import defaultdict
    
    reader = csv.reader(StringIO(tsv_string), delimiter='\t', quotechar='"')
    headers = next(reader)
    
    if as_columns:
        columns = defaultdict(list)
        for row in reader:
            for header, value in zip(headers, row + [''] * (len(headers) - len(row))):
                columns[header].append(value)
        return dict(columns)
    else:
        return [
            {header: value for header, value in zip(headers, row + [''] * (len(headers) - len(row)))}
            for row in reader
        ]


@dataclass
class TabularOutput(Output):
    fields: List[Output] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.fields = [
            Output(**x) if isinstance(x, dict) else x
            for x in self.fields
        ]

        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

        # Convert any dict evaluations to Evaluation objects
        self.evaluations = [
            eval_factory(
                field=self.name,
                field_description=self.description,
                inputs=x["inputs"] if "inputs" in x else self.inputs,
                **{k: v for k, v in x.items() if k != "inputs"}
            ) if isinstance(x, dict) else x
            for x in self.evaluations
        ]

    @property
    def definition(self) -> str:
        """Return a formatted definition string"""
        txt = [self.xml, self.description]
        txt.append("\nFormatted as a tab-separated-values table with a header row and the following columns (and requirements):\n")

        samples = []
        for x in self.fields:
            desc = [f"- {x.name}: {x.description}"]
            evals = [y for y in x.evaluations if not y.hidden]
            if evals:
                desc.append("\n".join([f"  - {evl.requirement}" for evl in evals]))
            samples.append("\n".join(desc))
        txt.append("\n".join(samples))

        evals = [x for x in self.evaluations if not x.hidden]
        txt.append(f"\nTable Requirements:")
        txt.append("\n".join([f"- {evl.requirement}" for evl in evals]))
        txt.append("- Multi-line strings should be enclosed in double quotes. Newline and tab characters should not be escaped.")
        txt.append("- Make sure to include a closing XML tag at the end of the table.")
        txt.append(self.xml_close)
        return "\n".join(txt)

    def process(self, x):
        return parse_tsv_string(x, as_columns=False)


def parse_jsonl_string(jsonl_string, as_columns=True):
    """
    Parse a JSON Lines string and return data in either columnar or row-based format.
    
    Args:
        jsonl_string (str): String containing JSON Lines data
        as_columns (bool): If True, return dict of lists (columnar format)
                         If False, return list of dicts (row format)
        
    Returns:
        Union[dict, list]: Either:
            - dict mapping column names to lists of values (if as_columns=True)
            - list of dictionaries, each representing a row (if as_columns=False)
    """
    import json
    from collections import defaultdict

    if as_columns:
        columns = defaultdict(list)
        
        # Split into lines and filter out empty ones
        lines = (line for line in jsonl_string.splitlines() if line.strip())
        
        # Parse each line as JSON
        for line in lines:
            row = json.loads(line)
            for key, value in row.items():
                columns[key].append(value)
                
        return dict(columns)
    else:
        # Return list of dicts format
        return [
            json.loads(line)
            for line in jsonl_string.splitlines()
            if line.strip()
        ]


@dataclass
class JsonlinesOutput(Output):
    fields: List[Output] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.fields = [
            Output(**x) if isinstance(x, dict) else x
            for x in self.fields
        ]

        self.inputs = [
            Input(**x) if isinstance(x, dict) else x
            for x in self.inputs
        ]

        # Convert any dict evaluations to Evaluation objects
        self.evaluations = [
            eval_factory(
                field=self.name,
                field_description=self.description,
                inputs=x["inputs"] if "inputs" in x else self.inputs,
                **{k: v for k, v in x.items() if k != "inputs"}
            ) if isinstance(x, dict) else x
            for x in self.evaluations
        ]

    @property
    def definition(self) -> str:
        """Return a formatted definition string"""
        txt = [self.xml, self.description]
        txt.append("\nFormatted as a jsonlines table with the following columns (and requirements):\n")

        samples = []
        for x in self.fields:
            desc = [f"- {x.name}: {x.description}"]
            evals = [y for y in x.evaluations if not y.hidden]
            if evals:
                desc.append("\n".join([f"  - {evl.requirement}" for evl in evals]))
            samples.append("\n".join(desc))
        txt.append("\n".join(samples))

        evals = [x for x in self.evaluations if not x.hidden]
        txt.append(f"\nTable Requirements:")
        txt.append("\n".join([f"- {evl.requirement}" for evl in evals]))
        txt.append("- Be sure to include a closing XML tag at the end of the table.")
        txt.append(self.xml_close)
        return "\n".join(txt)

    def process(self, x):
        return parse_jsonl_string(x, as_columns=False)


def output_factory(type: str = "text", **kwargs):
    output_type = type.lower()
    output_types = {
        "text": Output,
        "json": JsonOutput,
        "jsonl": JsonlinesOutput,
        "jsonlines": JsonlinesOutput,
        "tabular": TabularOutput
    }
    if output_type not in output_types:
        raise ValueError(f"Unknown output type: {type}")
    output_class = output_types.get(output_type)
    return output_class(**kwargs)
