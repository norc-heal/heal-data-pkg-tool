from frictionless import describe
import pandas as pd
import json
import requests
import pipe

def everything_after(df, cols):
    # cols is a list of col names (list of strings)
    another = df.columns.difference(cols, sort=False).tolist()
    return df[cols + another]

def get_heal_csv_dd_cols(heal_json_dd_schema_url=None, required_first=True, return_df=False):

    ###########################################################################
    # get the latest version of the heal json dd schema to populate the 
    # heal csv dd template - user can update url in function call if necessary
    ###########################################################################
    
    if heal_dd_json_schema_url is None:
        heal_dd_json_schema_url = 'https://raw.githubusercontent.com/HEAL/heal-metadata-schemas/main/variable-level-metadata-schema/schemas/fields.json'
    
    r = requests.get(heal_dd_json_schema_url)
    heal_dd_json_schema = r.json()
    print(heal_dd_json_schema)

    my_df_col = []

    for p in list(heal_dd_json_schema['properties'].keys()):
        if 'properties' in heal_dd_json_schema['properties'][p].keys():
            for p2 in list(heal_dd_json_schema['properties'][p]['properties'].keys()):
                my_df_col.append(p+'.'+p2)
        else:
            my_df_col.append(p)
         

    if not required_first:
        if not return_df:
            return my_df_col
        else:
            return pd.DataFrame(columns=my_df_col)
    else: 
        heal_dd_df = pd.DataFrame(columns=my_df_col)
        ###########################################################################
        # get the required fields from the heal json dd schema and put those 
        # first in the heal csv dd template
        ###########################################################################

        required_col = heal_dd_json_schema['required']
        heal_dd_df = heal_dd_df.pipe(everything_after, required_col)
        if not return_df:
            return heal_dd_df.columns.values.tolist()
        else:
            return heal_dd_df

def infer_dd(input_csv_data):
    ###########################################################################
    # bring in a new tabular resource, infer minimal table schema/dd
    ###########################################################################

    resource = describe(input_csv_data)
    resource = resource.to_dict()

    csv_dd_df = pd.json_normalize(resource, record_path=['schema','fields'])
    return csv_dd_df

def add_dd_to_heal_dd_template(csv_dd_df,required_first=True,save_path):
    # csv_dd_df is a csv data dictionary - it can be user-created or come from running infer_dd function on a csv data file
    # if it is user-created, user must ensure that dd column names match those in the heal vlmd field properties
    # e.g. 'name', 'description', 'type', etc. 

    # save path is a string that must end in '.csv'
    
    # get empty df with col names for all the heal vlmd field properties (including 'sub' properties)
    # user can specify whether to put the required properties first but that's the default
    # this is an empty heal csv dd template df
    heal_dd_df = get_heal_csv_dd_cols(required_first=required_first,return_df=True)
    
    # concat the input csv dd to the empty heal csv dd template df to add any info from the user input dd to the 
    # heal template 
    heal_dd_df = pd.concat([heal_dd_df,csv_dd_df])
    
    if save_path:
        heal_dd_df.to_csv(save_path,index=False)

    return heal_dd_df
    
