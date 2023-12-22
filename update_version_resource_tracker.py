import pandas as pd
import os
from versions_resource_tracker import fieldNameMap

# step 0-1: import resource tracker


getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg-first"
getResourceTrk = os.path.join(getDir,"heal-csv-resource-tracker.csv")
#getResourceTrk = r"P:\3652\Common\HEAL\y3-task-b-data-sharing-consult\repositories\vivli-submission-from-data-pkg\vivli-test-study\dsc-pkg-first\heal-heal-csv-resource-tracker.csv"
print("hello")

if os.path.isfile(getResourceTrk):
    print("hi")
    resourceTrackerDf = pd.read_csv(getResourceTrk)
    resourceTrackerDf.fillna("", inplace = True)

    print(resourceTrackerDf)

    for key in fieldNameMap["properties"]:

        # if deprecated is true
        #   delete any field with current or former field name(s) 
        if fieldNameMap["properties"][key]["deprecated"]:
            deleteFieldNames = [key]
            if fieldNameMap["properties"][key]["formerNames"]:
                deleteFieldNames.extend(fieldNameMap["properties"][key]["formerNames"])
            resourceTrackerDf.drop(columns=deleteFieldNames, inplace=True, errors="ignore")

        # if deprecated is false
        else:
            # if field with current field name exists
                # leave field with current field name alone
                # delete any field with a former field name
            if key in resourceTrackerDf.columns: 

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
                        # create new field with current field name
                    if i==0:

                # if no former field name(s)
                #   create new field with current field name
                else: 

                               
                     


#           
#       
#            


        #print(key,"; ",fieldNameMap["properties"][key]["formerNames"])
# # step 1: delete deprecated fields, rename fields, add new fields  

# for each schema property:

# if deprecated is true
#   delete any field with current or former field name(s)
# if deprecated is false
#   if field with current field name exists
#       leave field with current field name alone
#       delete any field with a former field name
#   if field with current field name does not exist
#       if former field name(s)
#           if field with former field name exists
#               copy field with former field name and rename to current field name
#           if field with former field name does not exist
#               create new field with current field name
#       if no former field name(s)
#           create new field with current field name
#
# after looping through all schema properties with above,
# for all schema properties where deprecated is False, collect all former field names,
# and delete any fields with a former field name

# step 2: update enums

# for each (non-deprecated) schema property:

# if mapEnums is not empty
#   if enum value is in keys of mapEnums
#       replace enum value with value specified by corresponding key of mapEnums
#   if enum value is not in keys of mapEnums
#       replace enum value with empty/null
# if mapEnums is empty
#   do nothing

# step 3: update subfield names

# for each (non-deprecated) schema property:

# if formerSubNames is not empty
#   if value is a list of dictionaries
#       replace keys in list of dictionaries according to the mapping in formerSubNames
#       (https://stackoverflow.com/questions/54637847/how-to-change-dictionary-keys-in-a-list-of-dictionaries)

