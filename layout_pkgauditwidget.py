import csv, codecs # base python, no pip install needed
import os # base python, no pip install needed
 
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport 
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QFile, Qt

import sys # base python, no pip install needed

from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

from pathlib import Path # base python, no pip install needed

from healdata_utils.cli import convert_to_vlmd

#from frictionless import plugins # frictionless already installed as a healdata_utils dependency, no pip install needed
#from frictionless.plugins import remote
#from frictionless import describe

import pandas as pd # pandas already installed as a healdata_utils dependency, no pip install needed
import json # base python, no pip install needed
import pipe

import dsc_pkg_utils # local module, no pip install needed
from layout_csveditwidget import CSVEditWindow

import version_check
import version_update_tracker

import schema_results_tracker

class PkgAuditWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.pkgPath = None # Initialize with no working data package directory path
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        widget = QtWidgets.QWidget()
        
        # self.buttonCheckPkgVersions = QtWidgets.QPushButton(text="Check Package Versions",parent=self)
        # self.buttonCheckPkgVersions.clicked.connect(self.check_pkg_versions)

        self.buttonUpdatePkgVersions = QtWidgets.QPushButton(text="Update Package Versions",parent=self)
        self.buttonUpdatePkgVersions.clicked.connect(self.update_pkg_versions)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(self.buttonCheckPkgVersions)
        layout.addWidget(self.buttonUpdatePkgVersions)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def check_pkg_versions(self):
        print("check package versions")
        
        
        
    def update_pkg_versions(self):
        print("update package versions")

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check if update is necessary
        checkVersions = version_check.version_check(self.workingDataPkgDir)
        allUpToDate = checkVersions[0]
        message = checkVersions[1]
        collectDf = checkVersions[2]
      
        
        if not allUpToDate:
            # create a copy of working data pkg dir in which to do the update - 
            # at the end can clean up but don't want the possibility that the update fails and the original is corrupted in the process
            # if an update in progress folder already exists exit with informative message - this may indicate that the user had a previously failed update since a successful update would lead to clean up of this folder
            if not dsc_pkg_utils.copyDataPkgDirToUpdate(self.workingDataPkgDir):
                messageText = "<br>Updates are needed. However, an update of your working data package directory may already be in progress. Check for a folder in the same parent directory as your working data package directory that starts with \"dsc-pkg\" and ends with \"update-in-progress\". If this folder exists, an update may have been initiated but not completed. If you didn't purposely create or keep this folder, please delete this folder and then come back here and try to update again. <br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return
            else:
                messageText = "<br>Updates are needed. An \"update-in-progress\" version of your working data package directory has been successfully created - This copy will be used to perform the updates and will be cleaned up at the end of a successful update - You should see a new folder in the same parent directory as your working data package directory that starts with \"dsc-pkg\" and ends with \"update-in-progress\".<br><br>Working on updates..<br>"
                saveFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))

                #QApplication.processEvents() # print accumulated user status messages 
            
                # a copy of the working data package dir and the operational subdir has been created in the update in progress dir
                # need to update the tracker and json txt file paths in collectDf to reflect the versions in the update in progress dir
                # so that updates will be made to the versions in that dir instead of the original working data pkg dir
                updateDir = dsc_pkg_utils.getDataPkgDirToUpdate(self.workingDataPkgDir)

                # strip original working data pkg dir from filenames
                collectDf["file"] = [os.path.basename(p) for p in collectDf["file"]]
                # add update in progress working data pkg dir to filenames
                collectDf["file"] = [os.path.join(updateDir,p) for p in collectDf["file"]]

                
            if "tracker" in collectDf["fileType"].values:
                
                trackerDf = collectDf[collectDf["fileType"] == "tracker"]

                noResultsTracker = "resultsTracker" not in trackerDf["trackerType"].values
                print("noResultsTracker: ",noResultsTracker)

                trackerDf["fileStem"] = [Path(f) for f in trackerDf["file"]]
                trackerDf["fileStem"] = [f.stem for f in trackerDf["fileStem"]]
                
                noCollectAllResultsTracker = "heal-csv-results-tracker-collect-all" not in trackerDf["fileStem"]
                print("noCollectAllResultsTracker: ", noCollectAllResultsTracker)
                
                #if "resultsTracker" not in trackerDf["trackerType"].values:
                if noCollectAllResultsTracker:
                    if noResultsTracker:
                        messageText = "<br>A csv results tracker was not detected - Creating a \"collect all\" csv results tracker now...<br><br>This standard data package metadata file will be saved in your working data package directory as \"heal-csv-results-tracker-collect-all.csv\". This results tracker will collect all results you document as part of this data package, even if they will not be shared in the same publication.<br><br>When you start documenting results, they will be added to this \"collect all\" results tracker - If you add an associated publication for a result, a new results tracker will be created in the working data package directory for that publication (if it does not already exist) and the result will ALSO be added to this publication-specific results tracker.<br>"
                        self.userMessageBox.append(messageText)

                        # create a no user access subdir in working data pkg dir for operational files
                        operationalFileSubDir = os.path.join(updateDir,"no-user-access")
                        if not os.path.exists(operationalFileSubDir):
                            os.mkdir(operationalFileSubDir)
                            
                        metadataTypeList = ["results-tracker"]
                        metadataSchemaVersionList = [schema_results_tracker.schema_results_tracker["version"]]
                        
                        for metadataType, metadataSchemaVersion in zip(metadataTypeList,metadataSchemaVersionList):

                            versionTxtFileName = "schema-version-" + metadataType + ".txt"
                            with open(os.path.join(operationalFileSubDir,versionTxtFileName), "w") as text_file:
                                text_file.write(metadataSchemaVersion)

                    if not noResultsTracker:
                        messageText = "<br>At least one publication-specific csv results tracker was detected, but a \"collect all\" csv results tracker was NOT detected - Creating a \"collect all\" csv results tracker now...<br><br>This standard data package metadata file will be saved in your working data package directory as \"heal-csv-results-tracker-collect-all.csv\". This results tracker will collect all results you document as part of this data package, even if they will not be shared in the same publication.<br><br>Results you have already added to a publication-specific results tracker will be added to the newly created \"collect all\" results tracker. When you start documenting new results, they will be added to this \"collect all\" results tracker - If you add an associated publication for a new result, a new results tracker will be created in the working data package directory for that publication (if it does not already exist) and the result will ALSO be added to the publication-specific results tracker.<br>"
                        self.userMessageBox.append(messageText)

                    # create an empty results tracker, call it results tracker collect all,
                    # and save it in update dir 
                    props = dsc_pkg_utils.heal_metadata_json_schema_properties(metadataType=metadataType)
                    df = dsc_pkg_utils.empty_df_from_json_schema_properties(jsonSchemaProperties=props)

                    if metadataType == "results-tracker":
                        fName = "heal-csv-" + metadataType + "-collect-all.csv"
                    else:
                        fName = "heal-csv-" + metadataType + ".csv"
                    
                    df.to_csv(os.path.join(updateDir, fName), index = False) 

                    messageText = "<br>Successfully created and saved a \"collect all\" csv results tracker - If you've already added results, these results will be added to the newly created \"collect all\" results tracker a bit later in the update process, and moving forward, any new results you add will be added both to the \"collect all\" results tracker and to a publication-specific results tracker (if you add an associated publication to the result). If you have not yet added any results, once your working data package directory update is complete, you'll be ready to go to start adding results.<br>"
                    self.userMessageBox.append(messageText)
                
                messageText = "<br>The following csv trackers were detected:<br>" + "<br>".join(trackerDf["file"].tolist())
                self.userMessageBox.append(messageText)
                #QApplication.processEvents() # print accumulated user status messages 
                
                if "No" in trackerDf["upToDate"].values:
                    trackerDfNeedsUpdate = trackerDf[trackerDf["upToDate"] == "No"]

                    messageText = "<br>The following csv trackers need to be updated:<br>" + "<br>".join(trackerDfNeedsUpdate["file"].tolist())
                    self.userMessageBox.append(messageText)
                    #QApplication.processEvents() # print accumulated user status messages 
                    
                    if "Yes" in trackerDfNeedsUpdate["canBeUpdated"].values:
                        trackerDfCanBeUpdated = trackerDfNeedsUpdate[trackerDfNeedsUpdate["canBeUpdated"] == "Yes"]

                        messageText = "<br>The following csv trackers need to be updated AND can be updated:<br>" + "<br>".join(trackerDfCanBeUpdated["file"].tolist()) + "<br><br>Starting updates<br>"
                        self.userMessageBox.append(messageText)
                        QApplication.processEvents() # print accumulated user status messages 

                        # update the trackers here
                        trkPathList = trackerDfCanBeUpdated["file"].tolist()
                        trkTypeCamelCaseList = trackerDfCanBeUpdated["trackerType"].tolist()
                        trkUpdateStatusList = []
                        for p,t in zip(trkPathList,trkTypeCamelCaseList):
                            trkUpdateStatus = version_update_tracker.version_update_tracker(getTrk=p,trackerTypeCamelCase=t)
                            trkUpdateStatusList.append(trkUpdateStatus)
                            if trkUpdateStatus:
                                messageText = "<br>The following " + t + " was successfully updated:<br>" + p + "<br>"
                                saveFormat = '<span style="color:green;">{}</span>'
                                self.userMessageBox.append(saveFormat.format(messageText))

                                # update json txt annotation files that were added to the tracker by writing 
                                # new json txt annotation files based on contents of updated tracker
                                # 1) check if all json txt annotation files in working data pkg dir have been added to the tracker
                                # 2)    for those not added, check if valid
                                # 3)        for those not added, if valid, update json directly and add to tracker
                                # 4)        for those not added, if invalid, attempt to update the json directly anyway, and somehow alert user to check these files and correct them
                                # 5)    for those added, write new json txt annotation file based on updated tracker contents for the annotation
                                
                                # for results tracker, if a collect-all results tracker exists, skip updating json txt annotation 
                                # files based on results tracker if it's not the collect all results tracker - this prevent 
                                # duplicative work to update result json txt annotation files if in more than one results tracker 
                                # and prevents erroneous error messages that a json txt annotation file could not be updated in the 
                                # case that not all results are in all results trackers
                                if t == "resultsTracker":
                                    if not noCollectAllResultsTracker:
                                        currentFilePath = Path(p)
                                        currentFileStem = currentFilePath.stem
                                        currentFileStemStr = str(currentFileStem)
                                        if not currentFileStemStr == "heal-csv-results-tracker-collect-all":
                                            continue

                                print("reading in tracker")
                                trackerDf = pd.read_csv(p)
                                trackerDf.fillna("", inplace = True)
                                pd.to_datetime(trackerDf["annotationModTimeStamp"])
                                print(trackerDf)
                                
                                idCol = dsc_pkg_utils.trkDict[t]["id"]
                                idNumCol = dsc_pkg_utils.trkDict[t]["id"] + "Number"
                                jsonTxtPrefix = dsc_pkg_utils.trkDict[t]["jsonTxtPrefix"]
                                schema = dsc_pkg_utils.trkDict[t]["schema"]

                                # get the array type properties in this tracker
                                # when pulling in from tracker, they will have become stringified lists instead of 
                                # true lists and will be incorrectly converted into json if not updated appropriately
                                arrayTypeProps = []
                                for key in schema["properties"]:
                                    if schema["properties"][key]["type"] == "array":
                                        arrayTypeProps.append(key) 
                                print("arrayTypeProps: ",arrayTypeProps)

                                # get id nums based on updated tracker
                                # if the tracker is empty, id nums in tracker is empty list
                                if trackerDf.empty:
                                    idNumFromTrackerList = []
                                else:
                                    # make sure the id num is an integer here 
                                    trackerDf[idNumCol] = trackerDf[idNumCol].astype(int)
                                    # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
                                    # to get the latest annotation entry
                                    trackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
                                    trackerDf.drop_duplicates(subset=[idNumCol],keep="last",inplace=True)

                                    idNumFromTrackerList = trackerDf[idNumCol].tolist()
                                    #idNumFromTrackerList = [int(item) for item in idNumFromTrackerList] 
                                    print("idNumFromTrackerList: ",idNumFromTrackerList)
                                    
                                # get id nums based on annotation files that already exist
                                existingFileList = [filename for filename in os.listdir(updateDir) if filename.startswith(jsonTxtPrefix)]
                                print(existingFileList)

                                if existingFileList: # if the list is not empty
                                    existingFileStemList = [Path(filename).stem for filename in existingFileList]
                                    print(existingFileStemList)
                                    existingFileIdNumList = [int(filename.split(jsonTxtPrefix)[1]) for filename in existingFileStemList]
                                    print(existingFileIdNumList)
                                else: 
                                    existingFileIdNumList = []
                                
                                # get the id nums in just annotation file, just tracker, or both (list of json txt annotation files that have and have not already been added to tracker - also check if some annotations added to tracker with no corresponding annotation file)
                                if not idNumFromTrackerList:
                                    if not existingFileIdNumList:
                                        print("NO json txt annotation files, and NO annotations in the tracker - There are no json txt annotation files to update or write")
                                        continue
                                    else:
                                        # in tracker, no json txt annotation file - this shouldn't happen unless someone added to tracker manually or using another tool
                                        inTrackerNotInTxtFileIdNumList = []
                                        # in tracker, with corresponding json txt annotation file - this should be most common especially if using updated tool
                                        inTrackerInTxtFileIdNumList = []
                                        # NOT in tracker, with a json txt annotation file - this may happen if the using an old version of the tool that does not auto add to tracker OR if the json txt file failed validation during the add to tracker step
                                        notInTrackerInTxtFileIdNumList = existingFileIdNumList
                                else:
                                    if not existingFileIdNumList:
                                        # in tracker, no json txt annotation file - this shouldn't happen unless someone added to tracker manually or using another tool
                                        inTrackerNotInTxtFileIdNumList = idNumFromTrackerList
                                        # in tracker, with corresponding json txt annotation file - this should be most common especially if using updated tool
                                        inTrackerInTxtFileIdNumList = []
                                        # NOT in tracker, with a json txt annotation file - this may happen if the using an old version of the tool that does not auto add to tracker OR if the json txt file failed validation during the add to tracker step
                                        notInTrackerInTxtFileIdNumList = []
                                        print("NO json txt annotation files, but there ARE annotations in the tracker - There are no json txt annotation files to update, but we can try to write json txt annotation files de novo for the annotations already in the tracker")
                                    else:
                                        # in tracker, no json txt annotation file - this shouldn't happen unless someone added to tracker manually or using another tool
                                        inTrackerNotInTxtFileIdNumList = [n for n in idNumFromTrackerList if n not in existingFileIdNumList]
                                        # in tracker, with corresponding json txt annotation file - this should be most common especially if using updated tool
                                        inTrackerInTxtFileIdNumList = [n for n in existingFileIdNumList if n in idNumFromTrackerList]
                                        # NOT in tracker, with a json txt annotation file - this may happen if the using an old version of the tool that does not auto add to tracker OR if the json txt file failed validation during the add to tracker step
                                        notInTrackerInTxtFileIdNumList = [n for n in existingFileIdNumList if n not in idNumFromTrackerList]

                                print("inTrackerNotInTxtFileIdNumList: ",inTrackerNotInTxtFileIdNumList)
                                print("inTrackerInTxtFileIdNumList: ",inTrackerInTxtFileIdNumList)
                                print("notInTrackerInTxtFileIdNumList: ",notInTrackerInTxtFileIdNumList)

                                writeFromTrackerToTxtFileIdNumList = inTrackerNotInTxtFileIdNumList + inTrackerInTxtFileIdNumList
                                # writeFromTrackerToTxtFileIdNumStringList = [str(idNum) for idNum in writeFromTrackerToTxtFileIdNumList]
                                # writeFromTrackerToTxtFileFnameList = [jsonTxtPrefix + idNumString + ".txt" for idNumString in writeFromTrackerToTxtFileIdNumStringList]
                                
                                if writeFromTrackerToTxtFileIdNumList:
                                    writeFromTrackerToTxtFileDf = trackerDf[trackerDf[idNumCol].isin(writeFromTrackerToTxtFileIdNumList)]
                                    
                                    # if at the beginning of the udpate there was not a collect-all results tracker, then should be updating 
                                    # json txt files based on publication-specific results trackers if they exist, in this case, want to 
                                    # add results that exist in the publication-specific results trackers to the newly created collect-all
                                    # results tracker here
                                    if t == "resultsTracker":
                                        if noCollectAllResultsTracker:
                                            newCollectAllDf = pd.read_csv(os.path.join(updateDir,"heal-csv-results-tracker-collect-all.csv")) 
                                            newCollectAllDf = pd.concat([newCollectAllDf,writeFromTrackerToTxtFileDf],axis=0)  
                                            newCollectAllDf = newCollectAllDf[-(newCollectAllDf.astype('string').duplicated())]
                                            print("newCollectAllDf rows, without dupes: ", newCollectAllDf.shape[0])
                                            newCollectAllDf.to_csv(os.path.join(updateDir,"heal-csv-results-tracker-collect-all.csv"), mode='w', header=True, index=False)

                                    if arrayTypeProps:
                                        for a in arrayTypeProps:
                                            writeFromTrackerToTxtFileDf[a] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(x) for x in writeFromTrackerToTxtFileDf[a]]
                                        
                                    writeFromTrackerToTxtFileDfToJson = writeFromTrackerToTxtFileDf.to_json(orient="records")
                                    writeFromTrackerToTxtFileDfToJsonParsed = json.loads(writeFromTrackerToTxtFileDfToJson)
                                    
                                    messageText = "<br>It was used to successfully update the following json txt annotation files:<br>"

                                    #for n,p in zip(writeFromTrackerToTxtFileIdNumList,writeFromTrackerToTxtFileFnameList):
                                    for j in writeFromTrackerToTxtFileDfToJsonParsed:
                                        print(j)
                                        print(j[idCol])
                                        print(j[idNumCol])
                                        fname = jsonTxtPrefix + str(int(j[idNumCol])) + '.txt'
                                        fpath = os.path.join(updateDir,fname)
                                        jFinal = json.dumps(j, indent=4)
                                        print(jFinal)
                                        with open(fpath, "w") as outfile:
                                            outfile.write(jFinal)
                                        
                                        messageText = messageText + fpath + "<br>"  
                                    
                                    saveFormat = '<span style="color:green;">{}</span>'
                                    self.userMessageBox.append(saveFormat.format(messageText))

                                if notInTrackerInTxtFileIdNumList:
                                    notInTrackerInTxtFileIdNumStringList = [str(idNum) for idNum in notInTrackerInTxtFileIdNumList]
                                    notInTrackerInTxtFileFnameList = [jsonTxtPrefix + idNumString + ".txt" for idNumString in notInTrackerInTxtFileIdNumStringList]
                                    notInTrackerInTxtFileFpathList = [os.path.join(updateDir,fname) for fname in notInTrackerInTxtFileFnameList]

                                    # 1) add content from each of the json txt annotation files to a df
                                    # 2) write the df to file as a temporary tracker
                                    # 3) run update tracker function on that temp tracker file
                                    # 4) write updated json txt annotation files to file (overwriting old json txt annotation files)
                                    # 5) read in content from each of updated json txt annotation files, and check if valid against schema
                                    # 6) if valid add to appropriate tracker(s)

                                    # 1) add content from each of the json txt annotation files to a df
                                    # initialize an empty dataframe to collect data from each file in ifileName
                                    # one row will be added to collect_df for each valid file in ifileName
                                    collect_df = pd.DataFrame([])
                                    # load data from json txt annotation file and convert to python object
                                    for p1 in notInTrackerInTxtFileFpathList:
                                    
                                        data = json.loads(Path(p1).read_text())
                                        # convert json to pd df
                                        df = pd.json_normalize(data) # df is a one row dataframe
                                        #print(df)
                                        # add this file's data to the dataframe that will collect data across all json txt annotation data files
                                        collect_df = pd.concat([collect_df,df], axis=0) 
                                        #print("collect_df rows: ", collect_df.shape[0])

                                    # 2) write the df to file as a temporary tracker
                                    tempTrkPath = os.path.join(updateDir,"temp-tracker.csv")
                                    collect_df.to_csv(tempTrkPath, mode='w', header=True, index=False)
                                    
                                    # 3) run update tracker function on that temp tracker file
                                    tempTrkUpdateStatus = version_update_tracker.version_update_tracker(getTrk=tempTrkPath,trackerTypeCamelCase=t)
                                    
                                    # 4) write updated json txt annotation files to file (overwriting old json txt annotation files)
                                    if tempTrkUpdateStatus:
                                        print("reading in tracker")
                                        trackerDf = pd.read_csv(tempTrkPath)
                                        trackerDf.fillna("", inplace = True)
                                        pd.to_datetime(trackerDf["annotationModTimeStamp"])
                                        print(trackerDf)
                                        
                                        idCol = dsc_pkg_utils.trkDict[t]["id"]
                                        idNumCol = dsc_pkg_utils.trkDict[t]["id"] + "Number"
                                        jsonTxtPrefix = dsc_pkg_utils.trkDict[t]["jsonTxtPrefix"]
                                        schema = dsc_pkg_utils.trkDict[t]["schema"]

                                        # get the array type properties in this tracker
                                        # when pulling in from tracker, they will have become stringified lists instead of 
                                        # true lists and will be incorrectly converted into json if not updated appropriately
                                        arrayTypeProps = []
                                        for key in schema["properties"]:
                                            if schema["properties"][key]["type"] == "array":
                                                arrayTypeProps.append(key) 
                                        print("arrayTypeProps: ",arrayTypeProps)

                                        # # get id nums based on updated tracker
                                        # # if the tracker is empty, id nums in tracker is empty list
                                        # if trackerDf.empty:
                                        #     idNumFromTrackerList = []
                                        # else:
                                        #     # make sure the id num is an integer here 
                                        #     trackerDf[idNumCol] = trackerDf[idNumCol].astype(int)
                                        #     # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
                                        #     # to get the latest annotation entry
                                        #     trackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
                                        #     trackerDf.drop_duplicates(subset=[idNumCol],keep="last",inplace=True)

                                        #     idNumFromTrackerList = trackerDf[idNumCol].tolist()
                                        #     #idNumFromTrackerList = [int(item) for item in idNumFromTrackerList] 
                                        #     print("idNumFromTrackerList: ",idNumFromTrackerList)

                                        writeFromTrackerToTxtFileDf = trackerDf
                                        if arrayTypeProps:
                                            for a in arrayTypeProps:
                                                writeFromTrackerToTxtFileDf[a] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(x) for x in writeFromTrackerToTxtFileDf[a]]
                                            
                                        writeFromTrackerToTxtFileDfToJson = writeFromTrackerToTxtFileDf.to_json(orient="records")
                                        writeFromTrackerToTxtFileDfToJsonParsed = json.loads(writeFromTrackerToTxtFileDfToJson)
                                        
                                        messageText = "<br>A temporary " + t + " was used to successfully update the following json txt annotation files:<br>"

                                        #for n,p in zip(writeFromTrackerToTxtFileIdNumList,writeFromTrackerToTxtFileFnameList):
                                        for j in writeFromTrackerToTxtFileDfToJsonParsed:
                                            print(j)
                                            print(j[idCol])
                                            print(j[idNumCol])
                                            fname = jsonTxtPrefix + str(int(j[idNumCol])) + '.txt'
                                            fpath = os.path.join(updateDir,fname)
                                            jFinal = json.dumps(j, indent=4)
                                            print(jFinal)
                                            with open(fpath, "w") as outfile:
                                                outfile.write(jFinal)
                                            
                                            messageText = messageText + fpath + "<br>"  
                                        
                                        saveFormat = '<span style="color:green;">{}</span>'
                                        self.userMessageBox.append(saveFormat.format(messageText))

                                        # 5) read in content from each of updated json txt annotation files, and check if valid against schema - 
                                        # if valid collect into a df
                                        
                                        # initialize lists to collect valid and invalid files
                                        validFiles = []
                                        invalidFiles = []
                                        # initialize an empty dataframe to collect data from each file in ifileName
                                        # one row will be added to collect_df for each valid file in ifileName
                                        collect_df = pd.DataFrame([])
                                        # load data from json txt annotation file and convert to python object
                                        for p2 in notInTrackerInTxtFileFpathList:
                                        
                                            data = json.loads(Path(p2).read_text())
                                            # validate json txt annotation file content against schema
                                            # for results and resource tracker, this should be the dynamically created schema with experimentNameBelongsTo enum populated with experiment names from experiment tracker
                                            out = validate_against_jsonschema(data, self.schema) 
                                            if not out["valid"]:
                                                # add file to list of invalid files
                                                invalidFiles.append(p2)
                                                continue
                                            else: 
                                                # add file to list of valid files
                                                validFiles.append(p2) 
                                                # convert json to pd df
                                                df = pd.json_normalize(data) # df is a one row dataframe
                                                #print(df)
                                                # add this file's data to the dataframe that will collect data across all json txt annotation data files
                                                collect_df = pd.concat([collect_df,df], axis=0) 
                                                #print("collect_df rows: ", collect_df.shape[0])
                                        
                                        # 6) if valid add to appropriate tracker(s)

                                        if validFiles: 
                                            # open appropriate tracker, append collect_df, save
                                            print("add these valid files to tracker")

                                    messageText = "<br>The following json txt annotation files have not been added to the appropriate tracker(s). These json txt annotation files must be updated to the current schema version before they can be added to the tracker. It is also possible that they were originally not added to the tracker because they failed validation against the schema version under which they were originally created. Update capabilities for json txt annotation files as well as validation checks will be available in the near future. In the meantime, these json txt files cannot be added to the tracker AND they cannot be edited using this version of the tool. Please standby for tool updates that will help you to resolve these issues, and let us know that you are experiencing this issue - This will help us to prioritize this as a needed tool update:<br>" + "<br>".join(notInTrackerInTxtFileFpathList) + "<br"
                                    saveFormat = '<span style="color:red;">{}</span>'
                                    self.userMessageBox.append(saveFormat.format(messageText))


                            else:
                                messageText = "<br>The following " + t + " was NOT successfully updated:<br>" + p + "<br>"
                                saveFormat = '<span style="color:red;">{}</span>'
                                self.userMessageBox.append(saveFormat.format(messageText))
                            #QApplication.processEvents() # print accumulated user status messages 

                        # if all trackers of a specific type are successfully updated, 
                        # update the schema version operational txt file
                        trkUpdateStatusDf = pd.DataFrame({"trackerType":trkTypeCamelCaseList,"file":trkPathList,"updateStatus":trkUpdateStatusList}) 
                        for t in trkUpdateStatusDf["trackerType"].unique().tolist():
                            filterDf = trkUpdateStatusDf[trkUpdateStatusDf["trackerType"] == t]
                            if filterDf["updateStatus"].all():
                                trackerTypeHyphen = dsc_pkg_utils.trkDict[t]["trackerTypeHyphen"]
                                versionTxtFileName = "schema-version-" + trackerTypeHyphen + ".txt"
                                versionTxtFilePath = os.path.join(updateDir,"no-user-access",versionTxtFileName)
                                versionText = dsc_pkg_utils.trkDict[t]["updateSchemaMap"]["latestVersion"]

                                if os.path.isfile(versionTxtFilePath):
                                    with open(versionTxtFilePath, "r+") as text_file:
                                        # opening in r+ means pointer is initially at start of file
                                        text = text_file.read()
                                        # after reading pointer will be at end of file, so writing will result in append
                                        if not text.endswith('\n'):
                                            text_file.write('\n')
                                        text_file.write(versionText)
                                else:
                                    with open(versionTxtFilePath, "w") as text_file:
                                        text_file.write(versionText)
                    else:
                        messageText = "<br>None of the csv trackers that need to be updated can be updated. This is likely because schema version mapping files for these trackers are not up to date."
                        self.userMessageBox.append(messageText)
                         


                else:
                    messageText = "<br>All csv trackers are up to date - json txt file updates coming soon<br>"
                    saveFormat = '<span style="color:orange;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    
                    origDir = self.workingDataPkgDir
                    os.rename(origDir,origDir + "-archive")
                    os.rename(updateDir,origDir)
                    
                    messageText = "<br>Your original working Data Package Directory has been archived as the original directory name + \"-archive\" plus .<br>"
                    saveFormat = '<span style="color:green;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    return
            else:
                messageText = "<br>No csv trackers were detected - json txt file updates coming soon<br>"
                saveFormat = '<span style="color:orange;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                
                origDir = self.workingDataPkgDir
                os.rename(origDir,origDir + "-archive")
                os.rename(updateDir,origDir)
                
                messageText = "<br>Your original working Data Package Directory has been archived as \"archive-\" plus the original directory name.<br>"
                saveFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            
            origDir = self.workingDataPkgDir
            os.rename(origDir,origDir + "-archive")
            os.rename(updateDir,origDir)
            
            messageText = "<br>Your original working Data Package Directory has been archived as \"archive-\" plus the original directory name.<br>"
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
        else:

            messageText = "<br>All dsc files are up to date - no updates needed!<br>"
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

    