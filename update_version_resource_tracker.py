import pandas as pd
import numpy as np
import os
from versions_resource_tracker import fieldNameMap
from schema_resource_tracker import schema_resource_tracker
import dsc_pkg_utils

# print(key,"; ",fieldNameMap["properties"][key]["formerNames"])

# step 0: import resource tracker


getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg-first"
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
                                return 
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
                            return

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
            if ((fieldNameMap["properties"][key]["mapEnum"]) | (fieldMap["properties"][key]["deleteEnum"])):
                
                # get type of schema property
                propertyType = schema_resource_tracker["properties"][key]["type"]
                
                # if deleteEnums is not empty
                if fieldMap["properties"][key]["deleteEnum"]:
                    
                    deleteDict = dict.fromkeys(fieldMap["properties"][key]["deleteEnum"],"")
                    
                    if propertyType == "string": # each value in this column of the df is a string
                        # if string value is equal to any of the values from delete list, replace string with empty string
                        resourceTrackerDf[key] = resourceTrackerDf[key].replace(deleteDict)
                        
                    elif propertyType == "array": # each value in this column of the df is an array of strings
                        
                        # check list/array for any values in delete list, and replace with empty string
                        # then remove any empty strings from list/array 
                        resourceTrackerDf[key] = [[deleteDict.get(i,i) for i in x] for x in resourceTrackerDf[key]]
                        resourceTrackerDf[key] = [[i for i in x if i] for x in resourceTrackerDf[key]]
                    
                    else:
                        print(key, " is not a string or array of strings - I don't know how to delete enums for any other property types yet!")
                
                else:
                    print(key, " has no enum deletions to review")

                if fieldMap["properties"][key]["mapEnum"]: 

                    mapDict = {}
                    for mapKey in fieldMap["properties"][key]["mapEnum"]:
                        mapDict.update(dict.fromkeys(fieldMap["properties"][key]["mapEnum"][mapKey],mapKey))
                    
                    print("key: ",key,"; mapDict: ", mapDict)

                    if propertyType == "string": # each value in this column of the df is a string
                        # check if string is equal to any of the former values that have a mapping, if so, replace with mapping
                        resourceTrackerDf[key] = resourceTrackerDf[key].replace(mapDict)
                        
                    elif propertyType == "array": # each value in this column of the df is an array of strings
                        
                        # check list/array for any former values that have a mapping, if so, replace with mapping
                        resourceTrackerDf[key] = [[mapDict.get(i,i) for i in x] for x in resourceTrackerDf[key]]

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
                for subNameKey in fieldMap["properties"][key]["formerSubNames"]:
                    subNameDict.update(dict.fromkeys(fieldMap["properties"][key]["formerSubNames"][subNameKey],subNameKey))
                
                print("key: ",key,"; subNameDict: ", subNameDict)
                
                # get type of schema property
                propertyType = schema_resource_tracker["properties"][key]["type"]

                # if value is a dictionary
                if propertyType == "object": # each value in this column of the df is a dictionary
                    
                    resourceTrackerDf[key] = [dsc_pkg_utils.renameDictKeys(x,subNameDict) for x in resourceTrackerDf[key]]

                # if value is a list of dictionaries                     
                elif propertyType == "array": # each value in this column of the df is an array of dictionaries

                    resourceTrackerDf[key] = [{dsc_pkg_utils.renameDictKeys(i,subNameDict) for i in x} for x in resourceTrackerDf[key]]

                else:
                        print(key, " is not a dictionary object or an arrary of dictionary objects - I don't know how to map former sub field names for any other property types yet!")

    print("done updating; reordering to correct order")
    resourceTrackerDf = resourceTrackerDf[collectAllCurrentNamesOrdered]
    
    print("done updating; getting ready to save")          
    getResourceTrkUpdated = os.path.join(getDir,"heal-csv-resource-tracker-updated.csv")
    resourceTrackerDf.to_csv(getResourceTrkUpdated, index=False)


#       replace keys in list of dictionaries according to the mapping in formerSubNames
#       (https://stackoverflow.com/questions/54637847/how-to-change-dictionary-keys-in-a-list-of-dictionaries)                         

