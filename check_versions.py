import schema_experiment_tracker
import schema_resource_tracker
import schema_results_tracker

import versions_experiment_tracker
import versions_resource_tracker
import versions_results_tracker

from packaging import version
import pandas as pd
import os

# get the working data package dir path
getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg-first"

trkDict = {
    
    "experimentTracker":{
        "schema":schema_experiment_tracker.schema_experiment_tracker,
        "updateSchemaMap": versions_experiment_tracker.fieldNameMap,
        "oneOrMulti":"one",
        "trackerName":"heal-csv-experiment-tracker.csv",
        "txtJsonPrefix": "exp-trk-exp-"
    },
    "resourceTracker":{
        "schema": schema_resource_tracker.schema_resource_tracker,
        "updateSchemaMap": versions_resource_tracker.fieldNameMap,
        "oneOrMulti": "one",
        "trackerName":"heal-csv-resource-tracker.csv",
        "txtJsonPrefix": "resource-trk-resource-"
    },
    "resultsTracker":{
        "schema": schema_results_tracker.schema_results_tracker,
        "updateSchemaMap": versions_results_tracker.fieldNameMap,
        "oneOrMulti": "multi",
        "trackerName":"heal-csv-results-tracker-",
        "txtJsonPrefix": "result-trk-result-"
    }
    
}

cols = ["trackerType","schemaVersion","schemaMapVersion","file","fileSchemaVersion","upToDate","canBeUpdated","canBeUpdatedFully","message"]
collectDf = pd.DataFrame([],columns=cols)

for key in trkDict:
    print(key)
    
    # get the latest/current schema version
    schema = trkDict[key]["schema"]
    schemaVersion = schema["version"]
    print("schemaVersion: ",schemaVersion)
    schemaVersionParse = version.parse(schemaVersion)
    
    # get the latest schema map version (this could be behind the latest schema version if 
    # there's not yet a map to the latest version available)
    updateSchemaMap = trkDict[key]["updateSchemaMap"]
    schemaMapVersion = updateSchemaMap["latestVersion"]
    print("schemaMapVersion: ",schemaMapVersion)
    schemaMapVersionParse = version.parse(schemaMapVersion)

    if schemaMapVersionParse == schemaVersionParse:
        print("mapping file for ",key," is up to date, and can be used to update to latest schema version: ",schemaVersion)
    elif schemaMapVersionParse < schemaVersionParse:
        print("mapping file for ",key," is NOT up to date - it can NOT be used to update to latest schema version: ",schemaVersion, "\n however it can be used to update to schema version: ",schemaMapVersion)
    
    if trkDict[key]["oneOrMulti"] == "one":
        trkPathList = [os.path.join(getDir,trkDict[key]["trackerName"])]
    elif trkDict[key]["oneOrMulti"] == "multi":
        trkPathList = [os.path.join(getDir,f) for f in os.listdir(getDir) if f.startswith(trkDict[key]["trackerName"])]

    for t in trkPathList:    
        trkDf = pd.read_csv(t)
        if "schemaVersion" not in trkDf:
            trkVersion = "0.1.0" 
        else:
            trkVersion = trkDf["schemaVersion"][0]

        trkVersionParse = version.parse(trkVersion)

        if trkVersionParse == schemaVersionParse:
            upToDate = "Yes"
            canBeUpdated = "Not Applicable"
            canBeUpdatedFully = "Not Applicable"
            message = "File is up to date"
        elif trkVersionParse < schemaVersionParse:
            upToDate = "No"
            if trkVersionParse == schemaMapVersionParse:
                canBeUpdated = "No"
                canBeUpdatedFully = "Not Applicable"
                message = "File is NOT up to date, but it cannot be updated at this time because the current schema mapping file does not allow updating beyond the file's current schema version"
            elif trkVersionParse < schemaMapVersionParse:
                canBeUpdated = "Yes"
                if schemaMapVersionParse == schemaVersionParse:
                    canBeUpdatedFully = "Yes"
                    message = "File is NOT up to date, and it can be fully updated at this time - Updating will update this file to the latest schema version"
            
                elif schemaMapVersionParse < schemaVersionParse:
                    canBeUpdatedFully = "No"
                    message = "File is NOT up to date - It can be updated, but it cannot be FULLY updated at this time because the current mapping file does allow updating beyond the file's current version but does NOT allow updating to the latest schema version - Updating will update this file to the latest schema version for which the schema mapping file has been completed"
            
        addDf = pd.DataFrame([[key,schemaVersionParse,schemaMapVersionParse,t,trkVersionParse,upToDate,canBeUpdated,canBeUpdatedFully,message]], columns=cols)
        collectDf = pd.concat([collectDf,addDf],axis=0)
        
    
collectDf['updateCheckDateTime'] = pd.Timestamp("now")
print(collectDf)    



# import exp tracker - check if schema version col exists - 
# if not, then version is prior to point at which schema versioning was implemented - prior to v0.3.0
# if yes, then get version value from schema version col



# experimentTrkSchemaMapVersion = versions_experiment_tracker.fieldNameMap["latestVersion"]
# print(experimentTrkSchemaMapVersion)

# resourceTrkSchemaMapVersion = versions_resource_tracker.fieldNameMap["latestVersion"]
# print(resourceTrkSchemaMapVersion)

# resultsTrkSchemaMapVersion = versions_results_tracker.fieldNameMap["latestVersion"]
# print(resultsTrkSchemaMapVersion)