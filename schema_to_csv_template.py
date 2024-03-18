import json
import jsonschema2md
import os
import sys
import itertools

#################################################
from dsc_pkg_utils import heal_metadata_json_schema_properties
#from dsc_pkg_utils import heal_metadata_json_schema
from dsc_pkg_utils import empty_df_from_json_schema_properties

#from schema_experiment_tracker import schema_experiment_tracker
#from schema_resource_tracker import schema_resource_tracker
#from schema_results_tracker import schema_results_tracker

# md_experiment_tracker_props = ".\md_experiment_tracker_props.md"
# md_resource_tracker_props = ".\md_resource_tracker_props.md"
# md_results_tracker_props = ".\md_results_tracker_props.md"
# md_data_dictionary_props = ".\md_data_dictionary_props.md"

# schema_type_list = ["experiment-tracker","resource-tracker","results-tracker","data-dictionary"]
# #output_md_list = [".\md_experiment_tracker_props.md",".\md_resource_tracker_props.md",".\md_results_tracker_props.md",".\md_data_dictionary_props.md"]
# output_csv_list = [".\heal-csv-experiment-tracker.csv",".\heal-csv-resource-tracker.csv",".\heal-csv-results-tracker.csv",".\heal-csv-data-dictionary.csv"]


schema_type_list = ["experiment-tracker","resource-tracker","results-tracker","data-dictionary"]
output_csv_list = [".\heal-csv-experiment-tracker.csv",".\heal-csv-resource-tracker.csv",".\heal-csv-results-tracker.csv",".\heal-csv-data-dictionary.csv"]

#################################################

# input_schema = schema_results_tracker
# output_md = md_results_tracker

# input_schema = schema_experiment_tracker
# output_md = md_experiment_tracker

# input_schema = schema_resource_tracker
# output_md = md_resource_tracker

#################################################

for (schema_type, output_template) in zip(schema_type_list, output_csv_list):

    input_schema_props = heal_metadata_json_schema_properties(schema_type)
    
    print(input_schema_props)

    input_schema_props_df = empty_df_from_json_schema_properties(input_schema_props)

    print(input_schema_props_df)

    input_schema_props_df.to_csv(output_template, index=False)

    