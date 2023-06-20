from frictionless import describe
from frictionless import Resource
import pandas as pd
import json # base python, no pip install needed
import requests
import pipe
import os # base python, no pip install needed
import shutil # base python, no pip install needed
import healdata_utils
import pathlib
import jsonschema
from jsonschema import validate
import re
import itertools

from healdata_utils.schemas import healjsonschema, healcsvschema
from schema_resource_tracker import schema_resource_tracker
from schema_experiment_tracker import schema_experiment_tracker




def heal_metadata_json_schema_properties(metadataType):

    print(metadataType)

    if metadataType == "data-dictionary":
        props = healjsonschema["properties"]["data_dictionary"]["items"]["properties"]
        

    if metadataType == "resource-tracker":
        props = schema_resource_tracker["properties"]
        

    if metadataType == "experiment-tracker":
        props = schema_experiment_tracker["properties"]
        

    if metadataType not in ["data-dictionary","resource-tracker","experiment-tracker"]:
        print("metadata type not supported; metadataType must be one of data-dictionary, resource-tracker, experiment-tracker")
        return
    
    return props


def empty_df_from_json_schema_properties(jsonSchemaProperties):
    all_fields = []

    for key, value in jsonSchemaProperties.items():
        p_fullname_list = []
        print(key)
        try:
            p_block = jsonSchemaProperties[key]["properties"]
            p_list = list(p_block.keys())
            p_fullname_list = [key + "." + p for p in p_list]
            print(p_fullname_list)
        except KeyError:
            pass

        if p_fullname_list:
            all_fields.extend(p_fullname_list)
        else:
            all_fields.append(key)

    print(all_fields)
    df = pd.DataFrame(columns = all_fields)    
    return df




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
        #heal_json_dd_schema_url = 'https://raw.githubusercontent.com/HEAL/heal-metadata-schemas/main/variable-level-metadata-schema/schemas/jsonschema/fields.json'
         heal_json_dd_schema_url = healdata_utils.schemas.jsonschema_url

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
    #pkg_resources_path = os.path.join(pkg_path,"resources") # create a subdir in the pkg dir for schema and template resources

    
    # create the new package directory    
    try:
        os.makedirs(pkg_path, exist_ok = False)
        print("Directory '%s' created successfully" %pkg_dir_name)
        #os.mkdir(pkg_resources_path) # make the subdir for resources
    except OSError as error:
        print("Directory '%s' can not be created - check to see if the directory already exists")
        return

    
    # add template starter files to new package directory
    #source_folder = dsc_pkg_resource_dir_path
    

    # fetch all files
    #results_schemas = []
    #results_templates = []
    #results_resources = []
    #results_use = []

    #results_schemas += [each for each in os.listdir(source_folder) if each.endswith('schema.csv')]
    #print(results_schemas) 
    #results_templates += [each for each in os.listdir(source_folder) if each.endswith('template.csv')]
    #print(results_templates) 
    #results_resources = results_schemas + results_templates
    #print(results_resources)
    
    #results_use += [each for each in os.listdir(source_folder) if each.endswith('tracker.csv')]
    #print(results_use)

    #destination_folder = pkg_resources_path
    #for file_name in os.listdir(source_folder):
    #for file_name in results_resources:
    #    # construct full file path
    #    #source = source_folder + file_name
    #    #destination = destination_folder + file_name
    #    source = os.path.join(source_folder,file_name)
    #    destination = os.path.join(destination_folder,file_name)
    #    # copy only files
    #    if os.path.isfile(source):
    #        shutil.copy(source, destination)
    #        print('copied', file_name)

    destination_folder = pkg_path
    #for file_name in os.listdir(source_folder):
    #for file_name in results_use:
    #    # construct full file path
    #    #source = source_folder + file_name
    #    #destination = destination_folder + file_name
    #    source = os.path.join(source_folder,file_name)
    #    destination = os.path.join(destination_folder,file_name)
    #    # copy only files
    #    if os.path.isfile(source):
    #        shutil.copy(source, destination)
    #        print('copied', file_name)

    for metadataType in ["experiment-tracker", "resource-tracker"]:
        props = heal_metadata_json_schema_properties(metadataType=metadataType)
        df = empty_df_from_json_schema_properties(jsonSchemaProperties=props)

        fName = "heal-csv-" + metadataType + ".csv"
        df.to_csv(os.path.join(pkg_path, fName), index = False) 

    return pkg_path

def qt_object_properties(qt_object: object) -> dict:
    """
    source: https://stackoverflow.com/questions/50556216/pyqt5-get-list-of-all-properties-in-an-object-qpushbutton
    Create a dictionary of property names and values from a QObject.

    :param qt_object: The QObject to retrieve properties from.
    :type qt_object: object
    :return: Dictionary with format
        {'name': property_name, 'value': property_value}
    :rtype: dict
    """
    properties: list = []

    # Returns a list of QByteArray.
    button_properties: list = qt_object.dynamicPropertyNames()

    for prop in button_properties:
        # Decode the QByteArray into a string.
        name: str = str(prop, 'utf-8')

        # Get the property value from the button.
        value: str = qt_object.property(name)

        properties.append({'name': name, 'value': value})

    return properties

def validateJson(jsonData,jsonSchema):
    # source: https://pynative.com/python-json-validation/
    try:
        validate(instance=jsonData, schema=jsonSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True
    
def get_multi_like_file_descriptions(nameConvention,fileStemList):

    nameConventionExplanatoryList = re.findall('{(.+?)}', nameConvention) # list of items enclosed in curly braces
    print(nameConventionExplanatoryList)

    if nameConventionExplanatoryList: # check if user added any naming convention explanatory values in the correct format (between curly braces); if yes, continue, if no, print informative message and return

        nameConventionAllList = re.split('[/{/}]', nameConvention)
        nameConventionAllList = [l for l in nameConventionAllList if l] # list of items delimited by curly braces (either direction)
        print(nameConventionAllList)

        nameOnlyOneExplanatory = False # set default value as false
        # check for delimiters between naming convention explanatory variables - need these to parse filenames to descriptions
        # if length of two lists is same then no delimiters between explanatory values exist, but if list is length one this is handle-able  
        if len(nameConventionAllList) == len(nameConventionExplanatoryList):
            if len(nameConventionAllList) == 1:
                nameOnlyOneExplanatory = True
            else:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                return

        if not nameOnlyOneExplanatory:
            noDelim = 0
            for idx, l in enumerate(nameConventionAllList):
                beforeVal = None
                afterVal = None
                if l in nameConventionExplanatoryList:
                    if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                        afterVal = nameConventionAllList[idx + 1]
                    if idx != 0: # if not first element, get element before current element  
                        beforeVal = nameConventionAllList[idx - 1]
            
                    if afterVal:
                        if afterVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(l," and ",afterVal," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")

                    if beforeVal:
                        if beforeVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(beforeVal," and ",l," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
  
            if noDelim > 0:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                return


        allFilesDescribeList = [] 

        for i in fileStemList:
        
            oneFileDescribeList = []  

            if nameOnlyOneExplanatory:
                oneFileDescribe = nameConventionAllList[0] + ": " + i
            else: 
            
                for idx, l in enumerate(nameConventionAllList):
                    beforeVal = None
                    beforeValSplit = None
                    afterVal = None
                    afterValSplit = None
                    if l in nameConventionExplanatoryList:
                        if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                            afterVal = nameConventionAllList[idx + 1]
                        if idx != 0: # if not first element, get element first current element  
                            beforeVal = nameConventionAllList[idx - 1]
            
                        if afterVal:
                            if afterVal in i:
                                afterValSplit = i.split(afterVal)
                        
                            else:
                                print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",afterVal," as specified by the applied naming convention.")
                                continue

                        if beforeVal:
                            if beforeVal in i:
                                beforeValSplit = i.split(beforeVal)
                        
                            else:
                                print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",beforeVal," as specified by the applied naming convention.")
                                continue

                        if ((not afterValSplit) and (not beforeValSplit)):
                            print("the file named ", i, " does not conform to the specified naming convention. It does not contain string(s) specified by the applied naming convention. Exiting check of this file.")
                            break

                        if ((afterValSplit) and (not beforeValSplit)):
                            myVal = afterValSplit[0]

                        if ((not afterValSplit) and (beforeValSplit)):
                            myVal = beforeValSplit[1]
                    
                        if ((afterValSplit) and (beforeValSplit)):
                            myVal = afterValSplit[0]
                            myVal = myVal.split(beforeVal)[1]
                    
                        myDescribe = l + ": " + myVal
                        oneFileDescribeList.append(myDescribe)   
            
                oneFileDescribe = ', '.join(oneFileDescribeList)
                print(oneFileDescribe)    
            
            allFilesDescribeList.append(oneFileDescribe) 
            print(allFilesDescribeList) 
    
    return allFilesDescribeList  

    
