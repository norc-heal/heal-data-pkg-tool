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

class PkgAuditWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.pkgPath = None # Initialize with no working data package directory path
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        widget = QtWidgets.QWidget()
        
        self.buttonCheckPkgVersions = QtWidgets.QPushButton(text="Check Package Versions",parent=self)
        self.buttonCheckPkgVersions.clicked.connect(self.check_pkg_versions)

        self.buttonUpdatePkgVersions = QtWidgets.QPushButton(text="Update Package Versions",parent=self)
        self.buttonUpdatePkgVersions.clicked.connect(self.update_pkg_versions)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonCheckPkgVersions)
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
                messageText = "<br>An update of your working data package directory may already be in progress. Check for a folder in the same parent directory as your working data package directory that starts with \"dsc-pkg\" and ends with \"update-in-progress\". If this folder exists, an update may have been initiated but not completed. If you didn't purposely create or keep this folder, please delete this folder and then come back here and try to update again. <br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return
            else:
                messageText = "<br>An \"update-in-progress\" version of your working data package directory has been successfully created - This copy will be used to perform the updates and will be cleaned up at the end of a successful update - You shouls see a new folder in the same parent directory as your working data package directory that starts with \"dsc-pkg\" and ends with \"update-in-progress\".<br>"
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
                                print("reading in tracker")
                                trackerDf = pd.read_csv(p)
                                trackerDf.fillna("", inplace = True)
                                print(trackerDf)
                                
                                idNumCol = dsc_pkg_utils.trkDict[t]["id"] + "Number"
                                jsonTxtPrefix = dsc_pkg_utils.trkDict[t]["jsonTxtPrefix"]

                                # if the tracker is empty, just create a new empty tracker based on the current schema
                                if trackerDf.empty:
                                    idNumList = []
                                else: 
                                    idNumList = trackerDf[idNumCol].unique().tolist()
                                    print("idList: ",idList)
                                    idNumStringList = [str(idNum) for idNum in idNumList]
                                    jsonTxtFromTrackerList = [jsonTxtFromTrackerList + idNumString + ".txt" for idNumString in idNumStringList]
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
                                    with open(versionTxtFilePath, "a") as text_file:
                                        text = text_file.read()
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
                    return
            else:
                messageText = "<br>No csv trackers were detected - json txt file updates coming soon<br>"
                saveFormat = '<span style="color:orange;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return


        else:

            messageText = "<br>All dsc files are up to date - no updates needed!<br>"
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

    