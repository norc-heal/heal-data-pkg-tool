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
#from layout_annotateexpwidget import AnnotateExpWindow
from layout_scrollannotateexpwidget import ScrollAnnotateExpWindow

import jsonschema
from jsonschema import validate
from schema_experiment_tracker import schema_experiment_tracker

from healdata_utils.validators.jsonschema import validate_against_jsonschema
import datetime


class ExpTrkAddWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.schemaVersion = schema_experiment_tracker["version"]
        
        widget = QtWidgets.QWidget()
        
        #self.buttonAnnotateExp = QtWidgets.QPushButton(text="Annotate a new experiment",parent=self)
        self.buttonAnnotateExp = QtWidgets.QPushButton(text="Add a new experiment",parent=self)
        self.buttonAnnotateExp.clicked.connect(self.annotate_exp)

        self.buttonEditExp = QtWidgets.QPushButton(text="Edit an existing experiment",parent=self)
        self.buttonEditExp.clicked.connect(self.edit_exp)

        self.buttonAddBasedOnExp = QtWidgets.QPushButton(text="Add a new experiment based on an existing experiment",parent=self)
        self.buttonAddBasedOnExp.clicked.connect(self.annotate_exp_based_on)

        #self.buttonAddExp = QtWidgets.QPushButton(text="Add experiment to tracker",parent=self)
        self.buttonAddExp = QtWidgets.QPushButton(text="Batch add existing experiment(s) to tracker",parent=self)
        self.buttonAddExp.clicked.connect(self.add_exp)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()

        advanced_layout = QtWidgets.QVBoxLayout()
        advanced_layout.addWidget(self.buttonAddBasedOnExp)
        advanced_layout.addWidget(self.buttonAddExp)
        advanced_groupbox = QtWidgets.QGroupBox("Advanced")
        advanced_groupbox.setLayout(advanced_layout)
        
        layout.addWidget(self.buttonAnnotateExp)
        layout.addWidget(self.buttonEditExp)
        #layout.addWidget(self.buttonAddBasedOnExp)
        #layout.addWidget(self.buttonAddExp)
        layout.addWidget(advanced_groupbox)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def annotate_exp(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return
        
        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="experiment-tracker",trackerTypeMessageString="Experiment Tracker"):
            return

        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            self.w = ScrollAnnotateExpWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,workingDataPkgDir=self.workingDataPkgDir,mode="add")
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def edit_exp(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="experiment-tracker",trackerTypeMessageString="Experiment Tracker"):
            return

        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            #self.w.editState = True
            self.w = ScrollAnnotateExpWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, workingDataPkgDir=self.workingDataPkgDir, mode="edit")
            self.w.show()
            self.w.load_file()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def annotate_exp_based_on(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="experiment-tracker",trackerTypeMessageString="Experiment Tracker"):
            return

        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            #self.w.editState = True
            self.w = ScrollAnnotateExpWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, workingDataPkgDir=self.workingDataPkgDir, mode="add-based-on")
            self.w.show()
            self.w.load_file()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    
    def add_exp(self):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="experiment-tracker",trackerTypeMessageString="Experiment Tracker"):
            return

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
                messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, close the file, and try again. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

        # get result file path
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Result Txt Data file(s)",
        #        (QtCore.QDir.homePath()), "Text (*.txt)")

        # open files select file browse to working data package directory
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Experiment Txt Data file(s) from your working Data Package Directory",
               self.workingDataPkgDir, "Text (*.txt)")
        
        if ifileName:
          
            # # check that experiment tracker exists in working data pkg dir, if not, return
            # if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            #     messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br>"
            #     saveFormat = '<span style="color:red;">{}</span>'
            #     self.userMessageBox.append(saveFormat.format(messageText))
            #     return
            
            # # check that experiment tracker is closed (user doesn't have it open in excel for example)
            # try: 
            #     with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
            #         print("file is closed, proceed!!")
            # except PermissionError:
            #         messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, close the file, and try again. <br><br>"
            #         saveFormat = '<span style="color:red;">{}</span>'
            #         self.userMessageBox.append(saveFormat.format(messageText))
            #         return

            # check that all files are experiment annotation files, if not, return
            fileStemList = [Path(filename).stem for filename in ifileName]
            print(fileStemList)
            checkFileStemList = [stem.startswith("exp-trk-exp-") for stem in fileStemList]
            print(checkFileStemList)
            
            if not all(checkFileStemList):
                messageText = "<br>The files you selected may not all be experiment txt files. Experiment txt files must start with the prefix \"exp-trk-exp-\". <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            # just for the first annotation file selected for addition to the tracker, check to make sure it is 
            # in the working data pkg dir - if not return with informative message
            ifileNameCheckDir = ifileName[0]

            # if user selects a result txt file that is not in the working data pkg dir, return w informative message
            if Path(self.workingDataPkgDir) != Path(ifileNameCheckDir).parent:
                messageText = "<br>You selected an experiment txt file that is not in your working Data Package Directory; You must select an experiment txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #countFiles = len(ifileName)

            # initialize lists to collect valid and invalid files
            validFiles = []
            invalidFiles = []
            
            # initialize an empty dataframe to collect data from each file in ifileName
            # one row will be added to collect_df for each valid file in ifileName
            collect_df = pd.DataFrame([])
            
            for filename in ifileName:
                print(filename)

                # get exp id and filename stem
                ifileNameStem = Path(filename).stem
                IdNumStr = ifileNameStem.rsplit('-',1)[1]
                annotation_id = "exp-" + IdNumStr
                print("exp-id: ", annotation_id)
                
                # load data from annotation file and convert to python object
                #path = ifileName
                path = filename
                data = json.loads(Path(path).read_text())
                print(data)

                # validate annotation file json content against tracker json schema
                out = validate_against_jsonschema(data, schema_experiment_tracker)
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
                    messageText = "The following experiment file is NOT valid and will not be added to the Experiment Tracker file: " + filename + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + printErrAll + "\n\n\n"
                    
                    self.userMessageBox.append(messageText)
                    #return
                    # switch from return to break so that if user selects more than one file, and one is not valid, can skip to next file and continue instead of returning fully out of the function
                    #break
                    continue 

                # if valid, continue:
                else:
                    #messageText = "The following resource file is valid: " + ifileName
                    messageText = "The following experiment file is valid: " + filename
                    self.userMessageBox.append(messageText)

                    # add file to list of valid files
                    validFiles.append(ifileNameStem)
                    print("valid files:", validFiles)

                    # get result annotation file creation and last modification datetime
                    restrk_c_timestamp = os.path.getctime(filename)
                    restrk_c_datetime = datetime.datetime.fromtimestamp(restrk_c_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("restrk_c_datetime: ", restrk_c_datetime)
        
                    restrk_m_timestamp = os.path.getmtime(filename)
                    restrk_m_datetime = datetime.datetime.fromtimestamp(restrk_m_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("restrk_m_datetime: ", restrk_m_datetime)

                    # add_to_df_dict = {#"resultId":[resource_id],
                    #                 "experimentIdNumber": [int(IdNumStr)],  
                    #                 #"annotationCreateDateTime": [restrk_c_datetime],
                    #                 #"annotationModDateTime": [restrk_m_datetime],
                    #                 "annotationModTimeStamp": [restrk_m_timestamp]}


                    # add_to_df = pd.DataFrame(add_to_df_dict)

                    # convert json to pd df
                    df = pd.json_normalize(data) # df is a one row dataframe
                    print(df)
                    df["annotationCreateDateTime"][0] = restrk_c_datetime
                    df["annotationModDateTime"][0] = restrk_m_datetime
                    df["experimentIdNumber"][0] = int(IdNumStr)
                    df["annotationModTimeStamp"][0] = restrk_m_timestamp
                    print(df)
                    # df = pd.concat([df,add_to_df], axis = 1) # concatenate cols to df; still a one row dataframe
                    # print(df)

                    collect_df = pd.concat([collect_df,df], axis=0) # add this files data to the dataframe that will collect data across all valid data files
                    print("collect_df rows: ", collect_df.shape[0])

                    
        else: 
            print("you have not selected any files; returning")
            messageText = "<br>You have not selected any experiment files to add to the experiment tracker. Please select at least one experiment file to add."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # once you've looped through all selected files, if none are valid, print an informative message for the user listing
        # which files did not pass validation and exit
        if not validFiles:
            messageText = "The contents of the Experiment file(s): " + "\n\n\n" + ', '.join(invalidFiles) + "\n\n\n" + "cannot be added to an Experiment Tracker file because they did not pass validation. Please review the validation errors for the file(s) printed above." + "Exiting \"Add Experiment\" function now." 
            self.userMessageBox.append(messageText)
            return

        
        
        # you should now have collected one row of data from each valid data file and collected it into collect_df dataframe
        # now get location of dsc pkg dir, check if appropriate results trackers already exist, if not create them, then add
        # results to appropriate results trackers

        # no longer need to ask user to browse to dsc data package dir - instead use working data package dir set by user in data package tab of tool
        #dscDirPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your result(s) will be auto-added to appropriate Results Tracker(s) there!')
        dscDirPath = self.workingDataPkgDir
        

        # this check should no longer be necessary
        if not dscDirPath:
            messageText = "You have not selected a directory. Please select your DSC Data Package Directory. If you have not yet created a DSC Data Package Directory, use the \"Create New Data Package\" button on the \"Create\" sub-tab of the \"Data Package\" tab to create a DSC Data Package Directory. You can then come back here and try adding your experiment file(s) again! <br><br>Exiting \"Add Experiment\" function now."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        

        # get tracker path
        trackerPath = os.path.join(dscDirPath,"heal-csv-experiment-tracker.csv")
        #parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Resource Tracker File lives here!')
        # resultsTrackerPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Results Tracker File to which you would like to add the Input Result Txt Data file(s)",
        #        (QtCore.QDir.homePath()), "CSV (*.csv *.tsv)")
               
        
        # if result tracker file selected, append the pd data object from the experiment file as a new row in the experiment tracker file
        # if doesn't exist, print error/info message and exit
        if trackerPath:

            #resultsTrackerPathStem = Path(resultsTrackerPath).stem

            if os.path.isfile(trackerPath):

            
                output_path = trackerPath
                all_df = pd.read_csv(output_path)
                #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
                all_df = pd.concat([all_df, collect_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
                all_df.sort_values(by = ["experimentIdNumber"], inplace=True)
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
                    messageText = "The contents of the Experiment file(s): <br><br>" + ', '.join(invalidFiles) + "<br><br>cannot be added to an Experiment Tracker file because they did not pass validation. Please review the validation errors printed above." 
                    errorFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(errorFormat.format(messageText))
            
                messageText = "The contents of the Experiment file(s): <br><br>" + ', '.join(validFiles) + "<br><br>were added as an experiment(s) to the Experiment Tracker file: <br><br>" + output_path
                errorFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
        
            else:
                messageText = "There is not a valid HEAL formatted experiment tracker file in the current working Data Package Directory."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
                return
        # else:
        #     messageText = "You have not selected a results tracker file. Please select a results tracker file to which to add your results. If you have not yet created a results tracker file, use the \"Create Results Tracker\" button on the \"Add Results\" sub-tab of the \"Results Tracker\" tab to create a results tracker, then save it as \"heal-csv-results-tracker-(name of multi-result file to which this results tracker applies)\". You can then come back here and try adding your result file(s) again! <br><br>Exiting \"Add Result\" function now."
        #     errorFormat = '<span style="color:red;">{}</span>'
        #     self.userMessageBox.append(errorFormat.format(messageText))
        #     return

            # # add dummies for whether or not each result is associated with any of the unique multiresult files listed in any of the results files
            # # this will allow filtering to the df that should be written to each result tracker file (each result tracker file is named after a specific unique multi result file)
            # # if a result tracker does not yet exist in the dsc pkg dir for each unique multiresult file listed across all result files, this fx will create the appropriate results tracker file
            # collect_df_cols = list(collect_df.columns)
            # print("collect_df_cols: ", collect_df_cols)

            # myDummies = collect_df["associatedFileMultiResultFile"].str.join('|').str.get_dummies()
            # print(list(myDummies.columns))

            # collect_df = pd.concat([collect_df, myDummies], axis = 1)

            # # get a list of any results trackers that already exist in dsc pkg dir
            # resultsTrkFileList = [filename for filename in os.listdir(dscDirPath) if filename.startswith("heal-csv-results-tracker")]
            # print(resultsTrkFileList)
            # resultsTrkFileList = [os.path.join(dscDirPath,filename) for filename in resultsTrkFileList]

            # #if resultsTrkFileList: # if the list is not empty
            # #    resultsTrkFileStemList = [Path(filename).stem for filename in resultsTrkFileList]
            # #    print(resultsTrkFileStemList)
            # #    
            # #else:
            # #    resultsTrkFileStemList = []

            # multiResultFileList = collect_df["associatedFileMultiResultFile"].explode().unique().tolist()
            # print("multi result file list: ",multiResultFileList)
            # multiResultFileStemList = [Path(filename).stem for filename in multiResultFileList]
            # print(multiResultFileStemList)
            # finalResultsTrkFileStemList = ["heal-csv-results-tracker-"+ filename + ".csv" for filename in multiResultFileStemList]
            # finalResultsTrkFileList = [os.path.join(dscDirPath,filename) for filename in finalResultsTrkFileStemList]
            # print("result tracker file list: ", resultsTrkFileList)
            # print("final result tracker file list: ", finalResultsTrkFileList)

            # if resultsTrkFileList:
            #     trkExist = [filename for filename in finalResultsTrkFileList if filename in resultsTrkFileList]
            #     print(trkExist)
            #     #trkExist = [os.path.join(dscDirPath,filename) for filename in trkExist]
            #     #print(trkExist)

            #     for t in trkExist:
            #         messageText = "Required results tracker already exists - new added results will be appended: <br>" + t
            #         #errorFormat = '<span style="color:red;">{}</span>'
            #         #self.userMessageBox.append(errorFormat.format(messageText))
            #         self.userMessageBox.append(messageText)
            # else: 
            #     trkExist = []


            # trkCreate = [filename for filename in finalResultsTrkFileList if filename not in resultsTrkFileList]
            # print(trkCreate)
            # #trkCreate = [os.path.join(dscDirPath,filename) for filename in trkCreate]
            # #print(trkCreate)

            # if trkCreate:
            #     df, _ = dsc_pkg_utils.new_results_trk()

            #     for t in trkCreate:
            #         df.to_csv(t, index = False) 
            #         messageText = "A new results tracker has been created - added results will be the first content: <br>" + t
            #         #errorFormat = '<span style="color:red;">{}</span>'
            #         #self.userMessageBox.append(errorFormat.format(messageText))
            #         self.userMessageBox.append(messageText)

            # else: 
            #     trkCreate = []

            # for m, t in zip(multiResultFileList, finalResultsTrkFileList):
            #     print(m,"; ",t)
            #     print_df = collect_df[collect_df[m] == 1]
            #     print(print_df.shape)
            #     print(print_df.columns)
            #     print_df = print_df[collect_df_cols]
            #     print(print_df.shape)
            #     print(print_df.columns)

            #     writeResultsList = print_df["resultId"].tolist()
            #     writeResultsFileList = ["result-trk-" + r for r in writeResultsList]
                
            #     output_path = t
            #     all_df = pd.read_csv(output_path)
            #     #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            #     all_df = pd.concat([all_df, print_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
            #     all_df.sort_values(by = ["resultIdNumber"], inplace=True)
            #     # drop any exact duplicate rows
            #     #all_df.drop_duplicates(inplace=True) # drop_duplicates does not work when df includes list vars
            #     # this current approach does not appear to be working at the moment
            #     print("all_df rows, with dupes: ", all_df.shape[0])
            #     all_df = all_df[-(all_df.astype('string').duplicated())]
            #     print("all_df rows, without dupes: ", all_df.shape[0])
            
            #     # before writing to file may want to check for duplicate result IDs and if duplicate result IDs, ensure that 
            #     # user wants to overwrite the earlier instance of the result ID in the results tracker - right now, dup entries 
            #     # for a result are all kept as long as not exact dup (i.e. at least one thing has changed)

            #     all_df.to_csv(output_path, mode='w', header=True, index=False)
            #     #df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

            #     messageText = "The contents of the Result file(s): <br><br>" + ', '.join(writeResultsFileList) + "<br><br>were added as a result(s) to the Results Tracker file: <br><br>" + output_path + "<br><br>"
            #     errorFormat = '<span style="color:green;">{}</span>'
            #     self.userMessageBox.append(errorFormat.format(messageText))

            # if invalidFiles:
            #     messageText = "The contents of the Result file(s): <br><br>" + ', '.join(invalidFiles) + "<br><br>cannot be added to a Results Tracker file because they did not pass validation. Please review the validation errors printed above." 
            #     errorFormat = '<span style="color:red;">{}</span>'
            #     self.userMessageBox.append(errorFormat.format(messageText))
            
            
            
    
    # def add_exp(self):

    #     # get experiment file path
    #     ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Input Experiment Txt Data file",
    #            (QtCore.QDir.homePath()), "Text (*.txt)")
        
    #     # load experiment file and convert to python object
    #     path = ifileName
    #     data = json.loads(Path(path).read_text())
    #     print(data)

    #     # validate experiment file json content against experiment tracker json schema
    #     out = validate_against_jsonschema(data, schema_experiment_tracker)
    #     print(out["valid"])
    #     print(out["errors"])

    #     # print validation errors and exit if not valid
    #     if out["valid"]:
    #         messageText = "The following experiment file is valid: " + ifileName
    #         self.userMessageBox.setText(messageText)
    #     else:
    #         messageText = "The following experiment file is NOT valid and will not be added to your Experiment Tracker file: " + ifileName + "\n\n\n" + "Validation errors are as follows: " + out["errors"] + "\n\n\n" + "Exiting \"Add Experiment\" function now."
    #         self.userMessageBox.setText(messageText)
    #         return
        
    #     # if valid, convert json to pd
    #     df = pd.json_normalize(data)
    #     print(df)

    #     # get data package directory path
    #     parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Experiment Tracker File lives here!')
        
    #     # check if experiment tracker file exists
    #     # if exists, append the pd data object from the experiment file as a new row in the experiment tracker file
    #     # if doesn't exist, print error/info message and exit
    #     if "heal-csv-experiment-tracker.csv" in os.listdir(parentFolderPath):
            
    #         output_path=os.path.join(parentFolderPath,"heal-csv-experiment-tracker.csv")
    #         df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

    #         messageText = messageText + "\n\n\n" + "The contents of the Experiment file: " + "\n\n\n" + ifileName + "\n\n\n" + "were added as an experiment to the Experiment Tracker file: " + "\n\n\n" + output_path
    #         self.userMessageBox.setText(messageText)
    #     else:
    #         messageText = messageText + "\n\n\n" + "No Experiment Tracker file exists at the designated directory. Are you sure this is a Data Package Directory? If you haven't yet created a Data Package Directory for your work, please head to the \"Data Package\" tab and use the \"Create new Data Package\" button to create your Data Package Directory. Your new Data Package Directory will contain your Experiment Tracker file. You can then come back here and try adding your experiment file again!" + "\n\n\n" + "Exiting \"Add Experiment\" function now."
    #         self.userMessageBox.setText(messageText)
    #         return
        
        
        
      

         
        
        


    
    