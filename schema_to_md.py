import json
import jsonschema2md
import os
import sys
import itertools

#################################################
#from dsc_pkg_utils import heal_metadata_json_schema_properties
from dsc_pkg_utils import heal_metadata_json_schema

#from schema_experiment_tracker import schema_experiment_tracker
#from schema_resource_tracker import schema_resource_tracker
#from schema_results_tracker import schema_results_tracker

# md_experiment_tracker_props = ".\md_experiment_tracker_props.md"
# md_resource_tracker_props = ".\md_resource_tracker_props.md"
# md_results_tracker_props = ".\md_results_tracker_props.md"
# md_data_dictionary_props = ".\md_data_dictionary_props.md"

schema_type_list = ["experiment-tracker","resource-tracker","results-tracker","data-dictionary"]
#output_md_list = [".\md_experiment_tracker_props.md",".\md_resource_tracker_props.md",".\md_results_tracker_props.md",".\md_data_dictionary_props.md"]
output_md_list = [".\md_experiment_tracker.md",".\md_resource_tracker.md",".\md_results_tracker.md",".\md_data_dictionary.md"]

#################################################

# input_schema = schema_results_tracker
# output_md = md_results_tracker

# input_schema = schema_experiment_tracker
# output_md = md_experiment_tracker

# input_schema = schema_resource_tracker
# output_md = md_resource_tracker

#################################################

for (schema_type, output_md) in zip(schema_type_list, output_md_list):

    #input_schema = heal_metadata_json_schema_properties(schema_type)
    input_schema = heal_metadata_json_schema(schema_type)

    print(input_schema)

    parser = jsonschema2md.Parser(
        examples_as_yaml=False,
        show_examples="all",
    )


    md_lines = parser.parse_schema(input_schema)
    print(''.join(md_lines))

    original_stdout = sys.stdout # save ref to original stdout of print

    with open(output_md,"w") as f:
        sys.stdout = f # change stdout to output md file we created
        print(''.join(md_lines))
        sys.stdout = original_stdout # reset stdout to original value

