import schema_experiment_tracker
import schema_resource_tracker
import schema_results_tracker

import versions_experiment_tracker
import versions_resource_tracker
import versions_results_tracker

from packaging import version
import pandas as pd
import os
import json

def version_check(workingDataPkgDir):

    # get the working data package dir path
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg-first"
    getDir = workingDataPkgDir

    # you're going to save this in the no user access folder since this is essentially an operational file
    saveUpdateStatusDir = os.path.join(getDir,"no-user-access")

    # add a little check to make sure the operational file no user access folder exists and if not, create it
    # these operational files and the folder to store them were a later addition
    if os.path.isdir(saveUpdateStatusDir):
        print("Exists")
    else:
        print("Doesn't exists")
        os.mkdir(saveUpdateStatusDir)

    # add a little check to make sure all the operational files are in the operational file no user access folder
    # since these were saved outside in the working data pkg dir for a short while
    operationalFilesList = ["resources-to-add.csv","annotation-mode-status.csv","share-status.csv"]
    for f in operationalFilesList:
        if f in os.listdir(getDir):
            os.rename(os.path.join(getDir,f), os.path.join(saveUpdateStatusDir,f))

    trkDict = {
        
        "experimentTracker":{
            "schema":schema_experiment_tracker.schema_experiment_tracker,
            "updateSchemaMap": versions_experiment_tracker.fieldNameMap,
            "oneOrMulti":"one",
            "trackerName":"heal-csv-experiment-tracker.csv",
            "jsonTxtPrefix": "exp-trk-exp-"
        },
        "resourceTracker":{
            "schema": schema_resource_tracker.schema_resource_tracker,
            "updateSchemaMap": versions_resource_tracker.fieldNameMap,
            "oneOrMulti": "one",
            "trackerName":"heal-csv-resource-tracker.csv",
            "jsonTxtPrefix": "resource-trk-resource-"
        },
        "resultsTracker":{
            "schema": schema_results_tracker.schema_results_tracker,
            "updateSchemaMap": versions_results_tracker.fieldNameMap,
            "oneOrMulti": "multi",
            "trackerName":"heal-csv-results-tracker-",
            "jsonTxtPrefix": "result-trk-result-"
        }
        
    }

    cols = ["trackerType","fileType","schemaVersion","schemaMapVersion","file","fileSchemaVersion","upToDate","canBeUpdated","canBeUpdatedFully","message"]
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

        print("trkPathList: ", trkPathList)

        if trkPathList:
            trkTypeList = ["tracker"] * len(trkPathList)
        
        jsonTxtPathList = [os.path.join(getDir,f) for f in os.listdir(getDir) if f.startswith(trkDict[key]["jsonTxtPrefix"])]
        print("jsonTxtPathList: ", jsonTxtPathList)

        if jsonTxtPathList:
            jsonTxtTypeList = ["json txt"] * len(jsonTxtPathList)

        if ((trkPathList) and (jsonTxtPathList)):
            pathList = trkPathList + jsonTxtPathList
            typeList = trkTypeList + jsonTxtTypeList
        else:
            if trkPathList:
                pathList = trkPathList
                typeList = trkTypeList
            elif jsonTxtPathList:
                pathList = jsonTxtPathList
                typeList = jsonTxtTypeList
            else:
                print("no files for ",key,"; moving on to next file type")
                continue

        for p,t in zip(pathList,typeList):  
            if t == "tracker":
                trkDf = pd.read_csv(p)
                if "schemaVersion" not in trkDf:
                    fileVersion = "0.1.0" 
                else:
                    fileVersion = trkDf["schemaVersion"][0]
            elif t == "json txt":
                with open(p, 'r') as file:
                    # Load JSON data from file
                    data = json.load(file)
                if "schemaVersion" not in list(data.keys()):
                    fileVersion = "0.1.0" 
                else:
                    fileVersion = data["schemaVersion"]


            fileVersionParse = version.parse(fileVersion)

            if fileVersionParse == schemaVersionParse:
                upToDate = "Yes"
                canBeUpdated = "Not Applicable"
                canBeUpdatedFully = "Not Applicable"
                message = "File is up to date"
            elif fileVersionParse < schemaVersionParse:
                upToDate = "No"
                if fileVersionParse == schemaMapVersionParse:
                    canBeUpdated = "No"
                    canBeUpdatedFully = "Not Applicable"
                    message = "File is NOT up to date, but it cannot be updated at this time because the current schema mapping file does not allow updating beyond the file's current schema version"
                elif fileVersionParse < schemaMapVersionParse:
                    canBeUpdated = "Yes"
                    if schemaMapVersionParse == schemaVersionParse:
                        canBeUpdatedFully = "Yes"
                        message = "File is NOT up to date, and it can be fully updated at this time - Updating will update this file to the latest schema version"
                
                    elif schemaMapVersionParse < schemaVersionParse:
                        canBeUpdatedFully = "No"
                        message = "File is NOT up to date - It can be updated, but it cannot be FULLY updated at this time because the current mapping file does allow updating beyond the file's current version but does NOT allow updating to the latest schema version - Updating will update this file to the latest schema version for which the schema mapping file has been completed"
                
            addDf = pd.DataFrame([[key,t,schemaVersionParse,schemaMapVersionParse,p,fileVersionParse,upToDate,canBeUpdated,canBeUpdatedFully,message]], columns=cols)
            collectDf = pd.concat([collectDf,addDf],axis=0)
            
        
    collectDf['updateCheckDateTime'] = pd.Timestamp("now")
    strTimeStamp = str(pd.Timestamp("now")).replace(" ","-").replace(":","-").replace(".","-")
    outFilename = "update-check-" + strTimeStamp + ".csv"
    collectDf.to_csv(os.path.join(saveUpdateStatusDir,outFilename), index = False)  
    
    message = ""

    print(collectDf.shape[0])

    if "No" in collectDf["upToDate"].values:

        allUpToDate = False

        messageDf1 = collectDf[collectDf["upToDate"] == "No"]
        message = message + "<br>1. Out of " + str(collectDf.shape[0]) + " total dsc-pkg files, " + str(messageDf1.shape[0]) + " files are NOT up to date."
        
        if "Yes" in messageDf1["canBeUpdated"].values:
            messageDf2 = messageDf1[messageDf1["canBeUpdated"] == "Yes"]
            message = message + "<br>2. Out of " + str(messageDf1.shape[0]) + " total dsc-pkg files that are NOT up to date, " + str(messageDf2.shape[0]) + " files can be updated based on available version mapping files."
        
            if "Yes" in messageDf2["canBeUpdatedFully"].values:
                messageDf3 = messageDf2[messageDf2["canBeUpdatedFully"] == "Yes"]
                message = message + "<br>2. Out of " + str(messageDf2.shape[0]) + " total dsc-pkg files that are NOT up to date and can be updated, " + str(messageDf3.shape[0]) + " files can be fully updated based on available version mapping files - Updating will update these files to the latest/current schema version."

            else: 
                message = message + "<br>2. Out of " + str(messageDf2.shape[0]) + " total dsc-pkg files that are NOT up to date and can be updated, 0 files can be fully updated based on available version mapping files - Updating these files to latest/current schema version will require that version mapping files be updated to reflect mapping to latest/current schema versions."


        else:
            message = message + "<br>2. Out of " + str(messageDf1.shape[0]) + " total dsc-pkg files that are NOT up to date, 0 files can be updated based on available version mapping files."
            print(messageDf1["canBeUpdated"])
            print("Yes" in messageDf1["canBeUpdated"])
    else: 
        allUpToDate = True
        message = message + "All dsc-pkg files are up to date"        

    return [allUpToDate, message]
    