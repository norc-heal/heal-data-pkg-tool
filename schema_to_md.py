import json
import jsonschema2md
import os
import sys

#################################################

from schema_experiment_tracker import schema_experiment_tracker
from schema_resource_tracker import schema_resource_tracker
from schema_results_tracker import schema_results_tracker

md_experiment_tracker = ".\md_experiment_tracker.md"
md_resource_tracker = ".\md_resource_tracker.md"
md_results_tracker = ".\md_results_tracker.md"

#################################################

# input_schema = schema_results_tracker
# output_md = md_results_tracker

# input_schema = schema_experiment_tracker
# output_md = md_experiment_tracker

input_schema = schema_resource_tracker
output_md = md_resource_tracker

#################################################

parser = jsonschema2md.Parser(
    examples_as_yaml=False,
    show_examples="all",
)
#with open("./examples/food.json", "r") as json_file:
#    md_lines = parser.parse_schema(json.load(json_file))
#print(''.join(md_lines))

md_lines = parser.parse_schema(input_schema)
print(''.join(md_lines))

original_stdout = sys.stdout # save ref to original stdout of print

with open(output_md,"w") as f:
    sys.stdout = f # change stdout to output md file we created
    print(''.join(md_lines))
    sys.stdout = original_stdout # reset stdout to original value

