import pandas as pd
import numpy as np
import os
import shutil
from versions_resource_tracker import fieldNameMap
from schema_resource_tracker import schema_resource_tracker
import dsc_pkg_utils
import json
import pathlib

# print(key,"; ",fieldNameMap["properties"][key]["formerNames"])

# pre-step A: get the working data package dir path
getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg-first"

# pre-step B: run the version check to see if files need update and can be updated
#check_versions.py 
# need to change check_versions.py script into a function, 
# import it here and then call it here; 
# then parse the update report - if at least one upToDate value is No and the canBeUpdated value for that file is Yes then continue with update
# if no upToDate values are No then quit with informative message "all files up to date; update unnecessary"
# if upToDate values contain at least one Yes but canBeUpdated value is No then quit with informative message "all files are not up to date but cannot be updated because up-to-date map files are not available - please update the following map files to proceed with update: "

# pre-step C: proceed with update after appropriate check in pre-step B - copy the working data package dir to an update in progress dir (don't mess with the original until the update is complete in case something fails)

getDirPath = pathlib.Path(getDir)

# get the stem/name of the working data package dir so that can reproduce it (e.g. may be dsc-pkg-my-study instead of just dsc-pkg, or dsc-pkg name may change over time)
getDirName = getDirPath.stem

# get the parent dir of the working data package dir path (should be the overall study folder)
getParentOfDirPath = getDirPath.parent

# in the overall study folder copy the working data pkg dir contents to an update in progress version of the working data pkg dir
getUpdateDirName = getDirName + "-update-in-progress" 
getUpdateDirPath = os.path.join(getParentOfDirPath,getUpdateDirName)

# path to source directory
src_dir = getDir
# path to destination directory
dest_dir = getUpdateDirPath
# getting all the files in the source directory
#files = os.listdir(src_dir)
shutil.copytree(src_dir, dest_dir)


# step 0: import resource tracker

getResourceTrk = os.path.join(getDir,"heal-csv-resource-tracker.csv")
#getResourceTrk = r"P:\3652\Common\HEAL\y3-task-b-data-sharing-consult\repositories\vivli-submission-from-data-pkg\vivli-test-study\dsc-pkg-first\heal-heal-csv-resource-tracker.csv"
print("hello")

if os.path.isfile(getResourceTrk):
    print("hi")
    resourceTrackerDf = pd.read_csv(getResourceTrk)
    resourceTrackerDf.fillna("", inplace = True)

    print(resourceTrackerDf)

    collectAllFormerNames = []
    collectAllCurrentNamesOrdered = [] # collect a list of current (non-deprecated) property names so that you can re-order based on the 'correct' order at the end of the update
    
    # step 1: for each schena property, delete deprecated fields, copy/rename undeprecated fields with former names, add new fields  
    
    print("working on step 1: updating field names")
    
    for key in fieldNameMap["properties"]:

        # if the property has former names, add them to a list that will collect all former field names 
        # across all properties for deletion all at once after looping through each property
        if fieldNameMap["properties"][key]["formerNames"]:
            collectAllFormerNames.extend(fieldNameMap["properties"][key]["formerNames"])

        # if deprecated is true
        #   delete any field with current or former field name(s) 
        if fieldNameMap["properties"][key]["deprecated"]:
            deleteFieldNames = [key]
            if fieldNameMap["properties"][key]["formerNames"]:
                deleteFieldNames.extend(fieldNameMap["properties"][key]["formerNames"])
            resourceTrackerDf.drop(columns=deleteFieldNames, inplace=True, errors="ignore")

        # if deprecated is false
        else:
            
            collectAllCurrentNamesOrdered.append(key) # collect a list of current (non-deprecated) property names so that you can re-order based on the 'correct' order at the end of the update
            
            # if field with current field name exists
            if key in resourceTrackerDf.columns: 
                
                # leave field with current field name alone
                # delete any field with a former field name
                if fieldNameMap["properties"][key]["formerNames"]:
                    deleteFieldNames = fieldNameMap["properties"][key]["formerNames"]
                    resourceTrackerDf.drop(columns=deleteFieldNames, inplace=True, errors="ignore")     
            
            # if field with current field name does not exist
            else:
            
                # if former field name(s)
                if fieldNameMap["properties"][key]["formerNames"]:

                    # if field with former field name exists
                        # copy field with former field name and rename to current field name
                        # (if more than one field with a former field name exists, error out with informative message)
                    formerFieldNames = fieldNameMap["properties"][key]["formerNames"]
                    i=0
                    for f in formerFieldNames:
                        
                        if f in resourceTrackerDf.columns:
                            i+=1
                            if i>1:
                                print("there is more than one field with a former name for the field currently named: ",key)
                                #return 
                            resourceTrackerDf[key] = resourceTrackerDf[f] 
                    
                    # if field with former field name does not exist
                        # create new field with current field name; fill with appropriate empty value
                    if i==0:
                        propertyType = schema_resource_tracker["properties"][key]["type"]

                        if propertyType == "string":
                            resourceTrackerDf[key] = "" # if the property is a string, empty is empty string
                        elif propertyType == "array":
                            resourceTrackerDf[key] = np.empty((len(resourceTrackerDf),0)).tolist() # if the property is an array, empty is empty list
                        else:
                            print("the following schema property is not a string or array type so i don't know how to create a new field with appropriate empty values: ", key)
                            #return

                # if no former field name(s)
                #   create new field with current field name; fill with appropriate empty value
                else: 
                    propertyType = schema_resource_tracker["properties"][key]["type"]
                        
                    if propertyType == "string":
                        resourceTrackerDf[key] = "" # if the property is a string, empty is empty string
                    elif propertyType == "array":
                        resourceTrackerDf[key] = np.empty((len(resourceTrackerDf),0)).tolist()

    # while looping through properties, if there were undeprecated fields still using a former field name,
    # that field was copied into a new field with the updated field name (instead of straight re-naming);
    # this is done in case an old field is parsed out into two new fields for which you might still want to 
    # copy the old values and map to new values for each new field (for example, this happened with the split from 
    # category sub results to category single result and category multi result)
    # HOWEVER, this approach means that following the loop through of properties, you have to go ahead and 
    # delete all fields with a former field name that remain in the df
    if collectAllFormerNames:
        resourceTrackerDf.drop(columns=collectAllFormerNames, inplace=True, errors="ignore")

    # step 2: update enums
    
    print("working on step 2: updating enums")
    
    # for each (non-deprecated) schema property:
    for key in fieldNameMap["properties"]:

        if not fieldNameMap["properties"][key]["deprecated"]:

            # if either deleteEnums or mapEnums is not empty
            #if ((fieldNameMap["properties"][key]["mapEnum"]) or (fieldNameMap["properties"][key]["deleteEnum"])):
            if ((bool(fieldNameMap["properties"][key]["mapEnum"])) or (bool(fieldNameMap["properties"][key]["deleteEnum"]))):
                
                # get type of schema property
                propertyType = schema_resource_tracker["properties"][key]["type"]
                
                # if deleteEnums is not empty
                if fieldNameMap["properties"][key]["deleteEnum"]:
                    
                    deleteDict = dict.fromkeys(fieldNameMap["properties"][key]["deleteEnum"],"")
                    
                    if propertyType == "string": # each value in this column of the df is a string
                        # if string value is equal to any of the values from delete list, replace string with empty string
                        resourceTrackerDf[key] = resourceTrackerDf[key].replace(deleteDict)
                        
                    elif propertyType == "array": # each value in this column of the df is an array of strings
                        
                        # check list/array for any values in delete list, and replace with empty string
                        # then remove any empty strings from list/array 
                        #resourceTrackerDf[key] = [[deleteDict.get(i,i) for i in x] for x in resourceTrackerDf[key]]
                        resourceTrackerDf[key] = [dsc_pkg_utils.mapArrayOfStrings(x,deleteDict) for x in resourceTrackerDf[key]]

                        #resourceTrackerDf[key] = [[i for i in x if i] for x in resourceTrackerDf[key]]
                        resourceTrackerDf[key] = [dsc_pkg_utils.deleteEmptyStringInArrayOfStrings(x) for x in resourceTrackerDf[key]]
                        
                    
                    else:
                        print(key, " is not a string or array of strings - I don't know how to delete enums for any other property types yet!")
                
                else:
                    print(key, " has no enum deletions to review")

                if fieldNameMap["properties"][key]["mapEnum"]: 

                    mapDict = {}
                    for mapKey in fieldNameMap["properties"][key]["mapEnum"]:
                        mapDict.update(dict.fromkeys(fieldNameMap["properties"][key]["mapEnum"][mapKey],mapKey))
                    
                    print("key: ",key,"; mapDict: ", mapDict)

                    if propertyType == "string": # each value in this column of the df is a string
                        # check if string is equal to any of the former values that have a mapping, if so, replace with mapping
                        resourceTrackerDf[key] = resourceTrackerDf[key].replace(mapDict)
                        
                    elif propertyType == "array": # each value in this column of the df is an array of strings
                        
                        # check list/array for any former values that have a mapping, if so, replace with mapping
                        #resourceTrackerDf[key] = [[mapDict.get(i,i) for i in x] for x in resourceTrackerDf[key]]
                        resourceTrackerDf[key] = [dsc_pkg_utils.mapArrayOfStrings(x,mapDict) for x in resourceTrackerDf[key]]


                    else:
                        print(key, " is not a string or array of strings - I don't know how to map enums for any other property types yet!")
                
                else:
                    print(key, " has no enum mappings to review")

            else:
                print(key, "has no enum deletions or mappings") 

        else:
            print(key, " is deprecated, no deletions or mapping of enums necessary")    
                
            
    # step 3: update subfield names
    
    print("working on step 3: updating subfield names")
    
    # for each (non-deprecated) schema property:
    for key in fieldNameMap["properties"]:

        if not fieldNameMap["properties"][key]["deprecated"]:

            # if formerSubNames is not empty
            if fieldNameMap["properties"][key]["formerSubNames"]:

                subNameDict = {}
                for subNameKey in fieldNameMap["properties"][key]["formerSubNames"]:
                    subNameDict.update(dict.fromkeys(fieldNameMap["properties"][key]["formerSubNames"][subNameKey],subNameKey))
                
                print("key: ",key,"; subNameDict: ", subNameDict)
                
                # get type of schema property
                propertyType = schema_resource_tracker["properties"][key]["type"]

                # if value is a dictionary
                if propertyType == "object": # each value in this column of the df is a dictionary
                    
                    resourceTrackerDf[key] = [dsc_pkg_utils.renameDictKeys(x,subNameDict) for x in resourceTrackerDf[key]]

                # if value is a list of dictionaries                     
                elif propertyType == "array": # each value in this column of the df is an array of dictionaries
                    print(key)
                    #resourceTrackerDf[key] = [{dsc_pkg_utils.renameDictKeys(i,subNameDict) for i in x} for x in resourceTrackerDf[key]]
                    #resourceTrackerDf.loc[bool(resourceTrackerDf[key]),resourceTrackerDf[key]] = [{dsc_pkg_utils.renameDictKeys(i,subNameDict) for i in x} for x in resourceTrackerDf[key]]
                    #resourceTrackerDf.loc[resourceTrackerDf[key] != '[]',resourceTrackerDf[key]] = [dsc_pkg_utils.renameListOfDictKeys(x,subNameDict) for x in resourceTrackerDf[key]]
                    resourceTrackerDf[key] = [dsc_pkg_utils.renameListOfDictKeys(x,subNameDict) for x in resourceTrackerDf[key]]
                    
                else:
                    print(key, " is not a dictionary object or an arrary of dictionary objects - I don't know how to map former sub field names for any other property types yet!")

    print("reordering to correct order")
    resourceTrackerDf = resourceTrackerDf[collectAllCurrentNamesOrdered]
    
    print("adding updated schema version")
    if "schemaVersion" in resourceTrackerDf.columns:
        resourceTrackerDf["schemaVersion"] = fieldNameMap["latestVersion"]
    else:
        print("has the name of the schema version property changed from schemaVersion? if so update the script to the new name to add the updated schema version")

    print("done updating; getting ready to save")          
    getResourceTrkUpdated = os.path.join(getDir,"heal-csv-resource-tracker-updated.csv")
    resourceTrackerDf.to_csv(getResourceTrkUpdated, index=False)

    print("saved")


#       replace keys in list of dictionaries according to the mapping in formerSubNames
#       (https://stackoverflow.com/questions/54637847/how-to-change-dictionary-keys-in-a-list-of-dictionaries)                         

