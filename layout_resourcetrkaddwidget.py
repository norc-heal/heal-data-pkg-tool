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
from layout_scrollannotateresourcewidget import ScrollAnnotateResourceWindow

import jsonschema
from jsonschema import validate
from schema_resource_tracker import schema_resource_tracker

from healdata_utils.validators.jsonschema import validate_against_jsonschema
import datetime


class ResourceTrkAddWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.schemaVersion = schema_resource_tracker["version"]
        
        widget = QtWidgets.QWidget()
        
        self.buttonAnnotateResource = QtWidgets.QPushButton(text="Add a new resource",parent=self)
        self.buttonAnnotateResource.clicked.connect(self.annotate_resource)

        self.buttonEditResource = QtWidgets.QPushButton(text="Edit an existing resource",parent=self)
        self.buttonEditResource.clicked.connect(self.edit_resource)

        self.buttonAddBasedOnResource = QtWidgets.QPushButton(text="Add a new resource based on an existing resource",parent=self)
        self.buttonAddBasedOnResource.clicked.connect(self.annotate_resource_based_on)

        self.buttonAddResource = QtWidgets.QPushButton(text="Batch add existing resource(s) to tracker",parent=self)
        self.buttonAddResource.clicked.connect(self.add_resource)

        

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()

        advanced_layout = QtWidgets.QVBoxLayout()
        advanced_layout.addWidget(self.buttonAddBasedOnResource)
        advanced_layout.addWidget(self.buttonAddResource)
        advanced_groupbox = QtWidgets.QGroupBox("Advanced")
        advanced_groupbox.setLayout(advanced_layout)
        
        layout.addWidget(self.buttonAnnotateResource)
        layout.addWidget(self.buttonEditResource)
        #layout.addWidget(self.buttonAddResource)
        layout.addWidget(advanced_groupbox)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def annotate_resource(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="resource-tracker",trackerTypeMessageString="Resource Tracker"):
            return

        # experiment tracker is needed to populate the enum of experimentNameBelongsTo schema property so perform some checks

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
            messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            #self.w.editState = False
            self.w = ScrollAnnotateResourceWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, workingDataPkgDir=self.workingDataPkgDir, mode="add")
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def edit_resource(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="resource-tracker",trackerTypeMessageString="Resource Tracker"):
            return

        # experiment tracker is needed to populate the enum of experimentNameBelongsTo schema property so perform some checks

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
            messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            #self.w.editState = True
            self.w = ScrollAnnotateResourceWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, workingDataPkgDir=self.workingDataPkgDir, mode="edit")
            self.w.show()
            self.w.load_file()


        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def annotate_resource_based_on(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="resource-tracker",trackerTypeMessageString="Resource Tracker"):
            return

        # experiment tracker is needed to populate the enum of experimentNameBelongsTo schema property so perform some checks

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
            messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            #self.w.editState = True
            self.w = ScrollAnnotateResourceWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, workingDataPkgDir=self.workingDataPkgDir, mode="add-based-on")
            self.w.show()
            self.w.load_file()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def add_resource(self):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="resource-tracker",trackerTypeMessageString="Resource Tracker"):
            return
            
        # experiment tracker is needed to populate the enum of experimentNameBelongsTo schema property (in this case for validation purposes) so perform some checks

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
            messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

        # check that resource tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-resource-tracker.csv")):
            messageText = "<br>There is no Resource Tracker file in your working Data Package Directory; Your working Data Package Directory must contain a Resource Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that resource tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-resource-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
                messageText = "<br>The Resource Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Resource Tracker file is open in Excel or similar application, close the file, and try again. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return
        
        # get resource(s) file path
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Resource Txt Data file(s)",
        #        (QtCore.QDir.homePath()), "Text (*.txt)")

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Resource Txt Data file(s)",
               self.workingDataPkgDir, "Text (*.txt)")
        
        if ifileName:

            # # check that resource tracker exists in working data pkg dir, if not, return
            # if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-resource-tracker.csv")):
            #     messageText = "<br>There is no Resource Tracker file in your working Data Package Directory; Your working Data Package Directory must contain a Resource Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br>"
            #     saveFormat = '<span style="color:red;">{}</span>'
            #     self.userMessageBox.append(saveFormat.format(messageText))
            #     return
            
            # # check that resource tracker is closed (user doesn't have it open in excel for example)
            # try: 
            #     with open(os.path.join(self.workingDataPkgDir,"heal-csv-resource-tracker.csv"),'r+') as f:
            #         print("file is closed, proceed!!")
            # except PermissionError:
            #         messageText = "<br>The Resource Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Resource Tracker file is open in Excel or similar application, close the file, and try again. <br><br>"
            #         saveFormat = '<span style="color:red;">{}</span>'
            #         self.userMessageBox.append(saveFormat.format(messageText))
            #         return

            
            # check that all files are resource annotation files, if not, return
            fileStemList = [Path(f).stem for f in ifileName]
            print(fileStemList)
            checkFileStemList = [s.startswith("resource-trk-resource-") for s in fileStemList]
            print(checkFileStemList)
            
            if not all(checkFileStemList):
                messageText = "<br>The files you selected may not all be resource txt files. Resource txt files must start with the prefix \"resource-trk-resource-\". <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            # just for the first annotation file selected for addition to the tracker, check to make sure it is 
            # in the working data pkg dir - if not return with informative message
            ifileNameCheckDir = ifileName[0]

            # if user selects a resource txt file that is not in the working data pkg dir, return w informative message
            if Path(self.workingDataPkgDir) != Path(ifileNameCheckDir).parent:
                messageText = "<br>You selected a resource txt file(s) that is not in your working Data Package Directory; You must select a resource txt file(s) that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #countFiles = len(ifileName)

            # initialize lists to collect valid and invalid files
            validFiles = []
            invalidFiles = []

            # dynamically update schema
            self.schema = schema_resource_tracker

            self.experimentNameList = []
            self.experimentNameList, _ = dsc_pkg_utils.get_exp_names(self=self, perResource=False) # gets self.experimentNameList
            print("self.experimentNameList: ",self.experimentNameList)
            if self.experimentNameList:
                #self.schema = self.add_exp_names_to_schema() # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList
                self.schema = dsc_pkg_utils.add_exp_names_to_schema(self=self) # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList

            
            # initialize an empty dataframe to collect data from each file in ifileName
            # one row will be added to collect_df for each valid file in ifileName
            collect_df = pd.DataFrame([])
            
            for filename in ifileName:
                print(filename)
                
                # get resource id and filename stem
                ifileNameStem = Path(filename).stem
                resIdNumStr = ifileNameStem.rsplit('-',1)[1]
                resource_id = "resource-" + resIdNumStr
                print("resource-id: ", resource_id)
                
                # load data from resource file and convert to python object
                #path = ifileName
                path = filename
                data = json.loads(Path(path).read_text())
                print(data)

                # # dynamically update schema
                # self.schema = schema_resource_tracker

                # self.experimentNameList = []
                # self.experimentNameList, _ = dsc_pkg_utils.get_exp_names(self=self) # gets self.experimentNameList
                # print("self.experimentNameList: ",self.experimentNameList)
                # if self.experimentNameList:
                #     #self.schema = self.add_exp_names_to_schema() # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList
                #     self.schema = dsc_pkg_utils.add_exp_names_to_schema(self=self) # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList


                # validate experiment file json content against experiment tracker json schema
                # out = validate_against_jsonschema(data, schema_resource_tracker)
                out = validate_against_jsonschema(data, self.schema)
                print(out["valid"])
                print(out["errors"])
                print(type(out["errors"]))

                
                # if not valid, print validation errors and exit 
                if not out["valid"]:

                    # add file to list of invalid files
                    invalidFiles.append(ifileNameStem)
                    
                    # get validation errors to print
                    printErrListSingle = []
                    # initialize the final full validation error message for this file to start with the filename
                    printErrListAll = [ifileNameStem]
                
                    for e in out["errors"]:
                        printErrListSingle.append(''.join(e["absolute_path"]))
                        printErrListSingle.append(e["validator"])
                        printErrListSingle.append(e["validator_value"])
                        printErrListSingle.append(e["message"])

                        print(printErrListSingle)
                        printErrSingle = '\n'.join(printErrListSingle)
                        printErrListAll.append(printErrSingle)

                        printErrListSingle = []
                        printErrSingle = ""
                    
                    printErrAll = '\n\n'.join(printErrListAll)
                
                    #messageText = "The following resource file is NOT valid and will not be added to your Resource Tracker file: " + ifileName + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + ', '.join(out["errors"]) + "\n\n\n" + "Exiting \"Add Resource\" function now."
                    messageText = "The following resource file is NOT valid and will not be added to your Resource Tracker file: " + filename + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + printErrAll + "\n\n\n"
                    
                    self.userMessageBox.append(messageText)
                    #return
                    # switch from return to break so that if user selects more than one file, and one is not valid, can skip to next file and continue instead of returning fully out of the function
                    #break
                    continue 

                # if valid, continue:
                else:
                    #messageText = "The following resource file is valid: " + ifileName
                    messageText = "The following resource file is valid: " + filename
                    self.userMessageBox.append(messageText)

                    # add file to list of invalid files
                    validFiles.append(ifileNameStem)
                    print("valid files:", validFiles)

                    # get resource tracker resource file creation and last modification datetime
                    #restrk_c_timestamp = os.path.getctime(ifileName)
                    restrk_c_timestamp = os.path.getctime(filename)
                    restrk_c_datetime = datetime.datetime.fromtimestamp(restrk_c_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("restrk_c_datetime: ", restrk_c_datetime)
        
                    #restrk_m_timestamp = os.path.getmtime(ifileName)
                    restrk_m_timestamp = os.path.getmtime(filename)
                    restrk_m_datetime = datetime.datetime.fromtimestamp(restrk_m_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("restrk_m_datetime: ", restrk_m_datetime)

                    # get resource creation and last modification datetime
                    res_c_timestamp = os.path.getctime(data["path"])
                    res_c_datetime = datetime.datetime.fromtimestamp(res_c_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("res_c_datetime: ", res_c_datetime)

                    res_m_timestamp = os.path.getmtime(data["path"])
                    res_m_datetime = datetime.datetime.fromtimestamp(res_m_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("res_m_datetime: ", res_m_datetime)

                    # add_to_df_dict = {#"resourceId":[resource_id],
                    #                 "resourceIdNumber": [int(resIdNumStr)],  
                    #                 #"resourceCreateDateTime": [res_c_datetime],
                    #                 #"resourceModDateTime": [res_m_datetime],
                    #                 "resourceModTimeStamp": [res_m_timestamp],
                    #                 #"annotationCreateDateTime": [restrk_c_datetime],
                    #                 #"annotationModDateTime": [restrk_m_datetime],
                    #                 "annotationModTimeStamp": [restrk_m_timestamp]}

                    # add_to_df = pd.DataFrame(add_to_df_dict)

                    # convert json to pd df
                    df = pd.json_normalize(data) # df is a one row dataframe
                    print(df)
                    df["annotationCreateDateTime"][0] = restrk_c_datetime
                    df["annotationModDateTime"][0] = restrk_m_datetime
                    df["resourceCreateDateTime"][0] = res_c_datetime
                    df["resourceModDateTime"][0] = res_m_datetime
                    df["resourceIdNumber"][0] = int(resIdNumStr)
                    df["resourceModTimeStamp"][0] = res_m_timestamp
                    df["annotationModTimeStamp"][0] = restrk_m_timestamp
                    # df = pd.concat([df,add_to_df], axis = 1) # concatenate cols to df; still a one row dataframe
                    # print(df)

                    collect_df = pd.concat([collect_df,df], axis=0) # add this files data to the dataframe that will collect data across all valid data files
                    print("collect_df rows: ", collect_df.shape[0])
        else: 
            print("you have not selected any files; returning")
            messageText = "<br>You have not selected any files; returning."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText)) 
            return

        # once you've looped through all selected files, if none are valid, print an informative message for the user listing
        # which files did not pass validation and exit
        if not validFiles:
            messageText = "The contents of the Resource file(s): " + "\n\n\n" + ', '.join(invalidFiles) + "\n\n\n" + "cannot be added to a Resource Tracker file because they did not pass validation. Please review the validation errors for the file(s) printed above." + "Exiting \"Add Resource\" function now." 
            self.userMessageBox.append(messageText)
            return

        # you should now have collected one row of data from each valid data file and collected it into collect_df dataframe
        # now get location of resource tracker, read in existing data in tracker, concat new data, sort, deduplicate and 
        # rewrite to file

        # no longer need to ask for this
        # get data package directory path
        #parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Resource Tracker File lives here!')
        parentFolderPath = self.workingDataPkgDir


        # check if resource tracker file exists
        # if exists, append the pd data object from the experiment file as a new row in the experiment tracker file
        # if doesn't exist, print error/info message and exit
        if "heal-csv-resource-tracker.csv" in os.listdir(parentFolderPath):
            
            output_path=os.path.join(parentFolderPath,"heal-csv-resource-tracker.csv")
            all_df = pd.read_csv(output_path)
            #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            all_df = pd.concat([all_df, collect_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
            all_df.sort_values(by = ["resourceIdNumber", "annotationModTimeStamp"], inplace=True)
            # drop any exact duplicate rows
            #all_df.drop_duplicates(inplace=True) # drop_duplicates does not work when df includes list vars
            # this current approach does not appear to be working at the moment
            print("all_df rows, with dupes: ", all_df.shape[0])
            all_df = all_df[-(all_df.astype('string').duplicated())]
            print("all_df rows, without dupes: ", all_df.shape[0])
            
            # before writing to file may want to check for duplicate resource IDs and if duplicate resource IDs, ensure that 
            # user wants to overwrite the earlier instance of the resource ID in the resource tracker - right now, dup entries 
            # for a resource are all kept as long as not exact dup (i.e. at least one thing has changed)

            all_df.to_csv(output_path, mode='w', header=True, index=False)
            #df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

            if invalidFiles:
                messageText = "The contents of the Resource file(s): " + "\n\n\n" + ', '.join(invalidFiles) + "\n\n\n" + "cannot be added to a Resource Tracker file because they did not pass validation. Please review the validation errors printed above." 
                self.userMessageBox.append(messageText)
            
            messageText = "The contents of the Resource file(s): " + "\n\n\n" + ', '.join(validFiles) + "\n\n\n" + "were added as a resource(s) to the Resource Tracker file: " + "\n\n\n" + output_path
            self.userMessageBox.append(messageText)
        else:
            messageText = "No Resource Tracker file exists at the designated directory. Are you sure this is a Data Package Directory? If you haven't yet created a Data Package Directory for your work, please head to the \"Data Package\" tab and use the \"Create new Data Package\" button to create your Data Package Directory. Your new Data Package Directory will contain your Resource Tracker file. You can then come back here and try adding your resource file again!" + "\n\n\n" + "Exiting \"Add Resource\" function now."
            self.userMessageBox.append(messageText)
            return
        


if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ResourceTrkAddWindow()
    window.show()
    sys.exit(app.exec_())   
      

         
        
        


    
    