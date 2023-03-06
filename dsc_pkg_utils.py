from frictionless import describe
import pandas as pd
import json # base python, no pip install needed
import requests
import pipe
import os # base python, no pip install needed
import shutil # base python, no pip install needed

def everything_after(df, cols):
    # convenience function to bring one or more cols in a dataframe to the front, while leaving all others in same order following
    # replicates functionality of dplyr 'everything' function - by: https://stackoverflow.com/users/2901002/jezrael
    # cols is a list of col names (list of strings)
    another = df.columns.difference(cols, sort=False).tolist()
    return df[cols + another]

def get_heal_csv_dd_cols(heal_json_dd_schema_url=None, required_first=True, return_df=False):

    ###########################################################################
    # get the latest version of the heal json dd schema to populate the 
    # heal csv dd template - user can update url in function call if necessary
    ###########################################################################
    
    if not heal_json_dd_schema_url:
        heal_json_dd_schema_url = 'https://raw.githubusercontent.com/HEAL/heal-metadata-schemas/main/variable-level-metadata-schema/schemas/fields.json'
    
    r = requests.get(heal_json_dd_schema_url)
    heal_json_dd_schema = r.json()
    print(heal_json_dd_schema)

    my_df_col = []

    for p in list(heal_json_dd_schema['properties'].keys()):
        if 'properties' in heal_json_dd_schema['properties'][p].keys():
            for p2 in list(heal_json_dd_schema['properties'][p]['properties'].keys()):
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

        required_col = heal_json_dd_schema['required']
        heal_dd_df = heal_dd_df.pipe(everything_after, required_col)
        if not return_df:
            return heal_dd_df.columns.values.tolist()
        else:
            return heal_dd_df

def infer_dd(input_csv_data):
    ###########################################################################
    # bring in a new tabular resource, infer minimal table schema/dd
    ###########################################################################
    # input csv data is a string file path to a csv data file

    resource = describe(input_csv_data)
    resource = resource.to_dict()

    csv_dd_df = pd.json_normalize(resource, record_path=['schema','fields'])
    return csv_dd_df

def add_dd_to_heal_dd_template(csv_dd_df,required_first=True,save_path=None):
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

def new_pkg(pkg_parent_dir_path,pkg_dir_name='dsc-pkg',dsc_pkg_resource_dir_path='./resources/'):
    
    #if not pkg_dir_name:
    #    pkg_dir_name = 'dsc-pkg'

    #if not dsc_pkg_resource_dir_path:
    #    dsc_pkg_resource_dir_path = './resources/'

    pkg_path = os.path.join(pkg_parent_dir_path,pkg_dir_name)

    # create the new package directory    
    try:
        os.makedirs(pkg_path, exist_ok = False)
        print("Directory '%s' created successfully" %pkg_dir_name)
    except OSError as error:
        print("Directory '%s' can not be created - check to see if the directory already exists")

    
    # add template starter files to new package directory
    source_folder = dsc_pkg_resource_dir_path
    destination_folder = pkg_path

    # fetch all files
    for file_name in os.listdir(source_folder):
        # construct full file path
        #source = source_folder + file_name
        #destination = destination_folder + file_name
        source = os.path.join(source_folder,file_name)
        destination = os.path.join(destination_folder,file_name)
        # copy only files
        if os.path.isfile(source):
            shutil.copy(source, destination)
            print('copied', file_name)

    return pkg_path

    


    
