import pandas as pd
import numpy as np
import os
import shutil

import dsc_pkg_utils
import json
import pathlib

# from versions_experiment_tracker import fieldNameMap
# from versions_resource_tracker import fieldNameMap
# from versions_results_tracker import fieldNameMap

# from schema_experiment_tracker import schema_experiment_tracker
# from schema_resource_tracker import schema_resource_tracker
# from schema_results_tracker import schema_results_tracker



# getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg-first"
# getUpdateDir = dsc_pkg_utils.getDataPkgDirToUpdate(workingDataPkgDir=getDir)
# getTrk = os.path.join(getUpdateDir,"heal-csv-resource-tracker.csv")

def version_update_tracker(getTrk,trackerTypeCamelCase):

    # step 0: import tracker
    
    if os.path.isfile(getTrk):

        # print("reading in tracker reference dictionary")
        # trkDict = dsc_pkg_utils.trkDict
        # print(trkDict)
        
        print("reading in tracker")
        trackerDf = pd.read_csv(getTrk)
        trackerDf.fillna("", inplace = True)
        print(trackerDf)

        # if the tracker is empty, just create a new empty tracker based on the current schema
        if trackerDf.empty:
            props = dsc_pkg_utils.heal_metadata_json_schema_properties(metadataType=dsc_pkg_utils.trkDict[trackerTypeCamelCase]["trackerTypeHyphen"])
            df = dsc_pkg_utils.empty_df_from_json_schema_properties(jsonSchemaProperties=props)

            df.to_csv(getTrk, index = False)
            return True


        # get the latest schema map version (this could be behind the latest schema version if 
        # there's not yet a map to the latest version available)
        #updateSchemaMap = trkDict[trackerTypeCamelCase]["updateSchemaMap"]
        fieldNameMap = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["updateSchemaMap"]

        collectAllFormerNames = []
        collectAllCurrentNamesOrdered = [] # collect a list of current (non-deprecated) property names so that you can re-order based on the 'correct' order at the end of the update
        
        # step 1: for each schema property, delete deprecated fields, copy/rename undeprecated fields with former names, add new fields  
        
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
                trackerDf.drop(columns=deleteFieldNames, inplace=True, errors="ignore")

            # if deprecated is false
            else:
                
                collectAllCurrentNamesOrdered.append(key) # collect a list of current (non-deprecated) property names so that you can re-order based on the 'correct' order at the end of the update
                
                # if field with current field name exists
                if key in trackerDf.columns: 
                    
                    # leave field with current field name alone
                    # delete any field with a former field name
                    if fieldNameMap["properties"][key]["formerNames"]:
                        deleteFieldNames = fieldNameMap["properties"][key]["formerNames"]
                        trackerDf.drop(columns=deleteFieldNames, inplace=True, errors="ignore")     
                
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
                            
                            if f in trackerDf.columns:
                                i+=1
                                if i>1:
                                    print("there is more than one field with a former name for the field currently named: ",key)
                                    return False
                                trackerDf[key] = trackerDf[f] 
                        
                        # if field with former field name does not exist
                            # create new field with current field name; fill with appropriate empty value
                        if i==0:
                            #propertyType = schema_resource_tracker["properties"][key]["type"]
                            propertyType = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["schema"]["properties"][key]["type"]

                            if propertyType == "string":
                                trackerDf[key] = "" # if the property is a string, empty is empty string
                            elif propertyType == "array":
                                trackerDf[key] = np.empty((len(trackerDf),0)).tolist() # if the property is an array, empty is empty list
                            elif propertyType == "integer":
                                trackerDf[key] = 0 # if the property is an integer, empty is zero (for now, maybe should be NaN?)
                                # note - add check for if id number column, if yes, and id column exists, calculate it from id column
                                idCol = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["id"]
                                idNumCol = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["id"] + "Number"
                                idPrefix = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["idPrefix"]
                                if key == idNumCol:
                                    trackerDf[key] = [int(idString.split(idPrefix)[1]) for idString in trackerDf[idCol]]
                            else:
                                print("the following schema property is not a string or array type so i don't know how to create a new field with appropriate empty values: ", key)
                                return False

                    # if no former field name(s)
                    #   create new field with current field name; fill with appropriate empty value
                    else: 
                        #propertyType = schema_resource_tracker["properties"][key]["type"]
                        propertyType = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["schema"]["properties"][key]["type"]

                            
                        if propertyType == "string":
                            trackerDf[key] = "" # if the property is a string, empty is empty string
                        elif propertyType == "array":
                            trackerDf[key] = np.empty((len(trackerDf),0)).tolist()

        # while looping through properties, if there were undeprecated fields still using a former field name,
        # that field was copied into a new field with the updated field name (instead of straight re-naming);
        # this is done in case an old field is parsed out into two new fields for which you might still want to 
        # copy the old values and map to new values for each new field (for example, this happened with the split from 
        # category sub results to category single result and category multi result)
        # HOWEVER, this approach means that following the loop through of properties, you have to go ahead and 
        # delete all fields with a former field name that remain in the df
        if collectAllFormerNames:
            trackerDf.drop(columns=collectAllFormerNames, inplace=True, errors="ignore")

        # step 2: update enums
        
        print("working on step 2: updating enums")
        
        # for each (non-deprecated) schema property:
        for key in fieldNameMap["properties"]:

            if not fieldNameMap["properties"][key]["deprecated"]:

                # if either deleteEnums or mapEnums is not empty
                #if ((fieldNameMap["properties"][key]["mapEnum"]) or (fieldNameMap["properties"][key]["deleteEnum"])):
                if ((bool(fieldNameMap["properties"][key]["mapEnum"])) or (bool(fieldNameMap["properties"][key]["deleteEnum"]))):
                    
                    # get type of schema property
                    #propertyType = schema_resource_tracker["properties"][key]["type"]
                    propertyType = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["schema"]["properties"][key]["type"]

                    
                    # if deleteEnums is not empty
                    if fieldNameMap["properties"][key]["deleteEnum"]:
                        
                        deleteDict = dict.fromkeys(fieldNameMap["properties"][key]["deleteEnum"],"")
                        
                        if propertyType == "string": # each value in this column of the df is a string
                            # if string value is equal to any of the values from delete list, replace string with empty string
                            trackerDf[key] = trackerDf[key].replace(deleteDict)
                            
                        elif propertyType == "array": # each value in this column of the df is an array of strings
                            
                            # check list/array for any values in delete list, and replace with empty string
                            # then remove any empty strings from list/array 
                            #resourceTrackerDf[key] = [[deleteDict.get(i,i) for i in x] for x in resourceTrackerDf[key]]
                            trackerDf[key] = [dsc_pkg_utils.mapArrayOfStrings(x,deleteDict) for x in trackerDf[key]]

                            #resourceTrackerDf[key] = [[i for i in x if i] for x in resourceTrackerDf[key]]
                            trackerDf[key] = [dsc_pkg_utils.deleteEmptyStringInArrayOfStrings(x) for x in trackerDf[key]]
                            
                        
                        else:
                            print(key, " is not a string or array of strings - I don't know how to delete enums for any other property types yet!")
                            return False
                    else:
                        print(key, " has no enum deletions to review")

                    if fieldNameMap["properties"][key]["mapEnum"]: 

                        mapDict = {}
                        for mapKey in fieldNameMap["properties"][key]["mapEnum"]:
                            mapDict.update(dict.fromkeys(fieldNameMap["properties"][key]["mapEnum"][mapKey],mapKey))
                        
                        print("key: ",key,"; mapDict: ", mapDict)

                        if propertyType == "string": # each value in this column of the df is a string
                            # check if string is equal to any of the former values that have a mapping, if so, replace with mapping
                            trackerDf[key] = trackerDf[key].replace(mapDict)
                            
                        elif propertyType == "array": # each value in this column of the df is an array of strings
                            
                            # check list/array for any former values that have a mapping, if so, replace with mapping
                            #resourceTrackerDf[key] = [[mapDict.get(i,i) for i in x] for x in resourceTrackerDf[key]]
                            trackerDf[key] = [dsc_pkg_utils.mapArrayOfStrings(x,mapDict) for x in trackerDf[key]]


                        else:
                            print(key, " is not a string or array of strings - I don't know how to map enums for any other property types yet!")
                            return False
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
                    #propertyType = schema_resource_tracker["properties"][key]["type"]
                    propertyType = dsc_pkg_utils.trkDict[trackerTypeCamelCase]["schema"]["properties"][key]["type"]


                    # if value is a dictionary
                    if propertyType == "object": # each value in this column of the df is a dictionary
                        
                        trackerDf[key] = [dsc_pkg_utils.renameDictKeys(x,subNameDict) for x in trackerDf[key]]

                    # if value is a list of dictionaries                     
                    elif propertyType == "array": # each value in this column of the df is an array of dictionaries
                        print(key)
                        #resourceTrackerDf[key] = [{dsc_pkg_utils.renameDictKeys(i,subNameDict) for i in x} for x in resourceTrackerDf[key]]
                        #resourceTrackerDf.loc[bool(resourceTrackerDf[key]),resourceTrackerDf[key]] = [{dsc_pkg_utils.renameDictKeys(i,subNameDict) for i in x} for x in resourceTrackerDf[key]]
                        #resourceTrackerDf.loc[resourceTrackerDf[key] != '[]',resourceTrackerDf[key]] = [dsc_pkg_utils.renameListOfDictKeys(x,subNameDict) for x in resourceTrackerDf[key]]
                        trackerDf[key] = [dsc_pkg_utils.renameListOfDictKeys(x,subNameDict) for x in trackerDf[key]]
                        
                    else:
                        print(key, " is not a dictionary object or an arrary of dictionary objects - I don't know how to map former sub field names for any other property types yet!")
                        return False

        print("reordering to correct order")
        trackerDf = trackerDf[collectAllCurrentNamesOrdered]
        
        print("adding updated schema version")
        if "schemaVersion" in trackerDf.columns: # it should be at this point, since it should have been added if not already present
            trackerDf["schemaVersion"] = fieldNameMap["latestVersion"]
        else:
            print("has the name of the schema version property changed from schemaVersion? if so update the script to the new name to add the updated schema version")
            return False

        print("done updating; getting ready to save")          
        #getTrkUpdated = os.path.join(getDir,"heal-csv-resource-tracker-updated.csv")
        trackerDf.to_csv(getTrk, index=False)

        print("saved")
        return True

    else:
        return False

    #       replace keys in list of dictionaries according to the mapping in formerSubNames
    #       (https://stackoverflow.com/questions/54637847/how-to-change-dictionary-keys-in-a-list-of-dictionaries)                         

