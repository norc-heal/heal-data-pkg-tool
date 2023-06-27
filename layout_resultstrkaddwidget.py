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

from frictionless import plugins # frictionless already installed as a healdata_utils dependency, no pip install needed
from frictionless.plugins import remote
from frictionless import describe

import pandas as pd # pandas already installed as a healdata_utils dependency, no pip install needed
import json # base python, no pip install needed
import requests # requests already installed as a healdata_utils dependency, no pip install needed
import pipe

import dsc_pkg_utils # local module, no pip install needed
from layout_scrollannotateresultwidget import ScrollAnnotateResultWindow

import jsonschema
from jsonschema import validate
from schema_results_tracker import schema_results_tracker

from healdata_utils.validators.jsonschema import validate_against_jsonschema
import datetime


class ResultsTrkAddWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonAnnotateResult = QtWidgets.QPushButton(text="Annotate a new result",parent=self)
        self.buttonAnnotateResult.clicked.connect(self.annotate_result)

        self.buttonAddResult = QtWidgets.QPushButton(text="Add result to tracker",parent=self)
        self.buttonAddResult.clicked.connect(self.add_result)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        
        layout.addWidget(self.buttonAnnotateResult)
        layout.addWidget(self.buttonAddResult)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def annotate_result(self,checked):
        if self.w is None:
            self.w = ScrollAnnotateResultWindow()
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def add_result(self):

        # get result file path
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Result Txt Data file(s)",
               (QtCore.QDir.homePath()), "Text (*.txt)")
        
        if ifileName:
            #countFiles = len(ifileName)

            # initialize lists to collect valid and invalid files
            validFiles = []
            invalidFiles = []
            
            # initialize an empty dataframe to collect data from each file in ifileName
            # one row will be added to collect_df for each valid file in ifileName
            collect_df = pd.DataFrame([])
            
            for filename in ifileName:
                print(filename)
                
                # get result id and filename stem
                ifileNameStem = Path(filename).stem
                IdNumStr = ifileNameStem.rsplit('-',1)[1]
                result_id = "result-" + IdNumStr
                print("result-id: ", result_id)
                
                # load data from result file and convert to python object
                #path = ifileName
                path = filename
                data = json.loads(Path(path).read_text())
                print(data)

                # validate experiment file json content against experiment tracker json schema
                out = validate_against_jsonschema(data, schema_results_tracker)
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
                    messageText = "The following result file is NOT valid and will not be added to your Resource Tracker file: " + filename + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + printErrAll + "\n\n\n"
                    
                    self.userMessageBox.append(messageText)
                    #return
                    # switch from return to break so that if user selects more than one file, and one is not valid, can skip to next file and continue instead of returning fully out of the function
                    #break
                    continue 

                # if valid, continue:
                else:
                    #messageText = "The following resource file is valid: " + ifileName
                    messageText = "The following result file is valid: " + filename
                    self.userMessageBox.append(messageText)

                    # add file to list of invalid files
                    validFiles.append(ifileNameStem)
                    print("valid files:", validFiles)

                    add_to_df_dict = {"result.id.num": [int(IdNumStr)]}

                    add_to_df = pd.DataFrame(add_to_df_dict)

                    # convert json to pd df
                    df = pd.json_normalize(data) # df is a one row dataframe
                    print(df)
                    df = pd.concat([df,add_to_df], axis = 1) # concatenate cols to df; still a one row dataframe
                    print(df)

                    collect_df = pd.concat([collect_df,df], axis=0) # add this files data to the dataframe that will collect data across all valid data files
                    print("collect_df rows: ", collect_df.shape[0])
        else: 
            print("you have not selected any files; returning")
            messageText = "<br>You have not selected any result files to add to the result tracker. Please select at least one result file to add."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # once you've looped through all selected files, if none are valid, print an informative message for the user listing
        # which files did not pass validation and exit
        if not validFiles:
            messageText = "The contents of the Resource file(s): " + "\n\n\n" + ', '.join(invalidFiles) + "\n\n\n" + "cannot be added to a Resource Tracker file because they did not pass validation. Please review the validation errors for the file(s) printed above." + "Exiting \"Add Result\" function now." 
            self.userMessageBox.append(messageText)
            return

        # you should now have collected one row of data from each valid data file and collected it into collect_df dataframe
        # now get location of resource tracker, read in existing data in tracker, concat new data, sort, deduplicate and 
        # rewrite to file

        # get result tracker path
        #parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Resource Tracker File lives here!')
        resultTrackerPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Result Tracker File to which you would like to add the Input Result Txt Data file(s)",
               (QtCore.QDir.homePath()), "Text (*.txt)")
               
        
        # if result tracker file selected, append the pd data object from the experiment file as a new row in the experiment tracker file
        # if doesn't exist, print error/info message and exit
        if resultTrackerPath:

            resultTrackerPathStem = Path(resultTrackerPath).stem

            if resultTrackerPathStem.startswith('heal-csv-result-tracker'):

            
                output_path = resultTrackerPath
                all_df = pd.read_csv(output_path)
                #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
                all_df = pd.concat([all_df, collect_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
                all_df.sort_values(by = ["result.id.num"], inplace=True)
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
                    messageText = "The contents of the Result file(s): <br><br>" + ', '.join(invalidFiles) + "<br><br>cannot be added to a Result Tracker file because they did not pass validation. Please review the validation errors printed above." 
                    errorFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(errorFormat.format(messageText))
            
                messageText = "The contents of the Result file(s): <br><br>" + ', '.join(validFiles) + "<br><br>were added as a result(s) to the Result Tracker file: <br><br>" + output_path
                errorFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
        
            else:
                messageText = "The file you selected does not appear to be a valid HEAL formatted result tracker file. Please select a valid HEAL formatted result tracker file to which to add your results. If you have not yest created a result tracker file, use the \"Create Result Tracker\" button on the \"Add Results\" sub-tab of the \"Result Tracker\" tab to create a result tracker, then save it as \"heal-csv-resource-tracker-(name of multi-result file to which this result tracker applies)\". You can then come back here and try adding your result file(s) again! <br><br>Exiting \"Add Result\" function now."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
                return
        else:
            messageText = "You have not selected a result tracker file. Please select a result tracker file to which to add your results. If you have not yest created a result tracker file, use the \"Create Result Tracker\" button on the \"Add Results\" sub-tab of the \"Result Tracker\" tab to create a result tracker, then save it as \"heal-csv-resource-tracker-(name of multi-result file to which this result tracker applies)\". You can then come back here and try adding your result file(s) again! <br><br>Exiting \"Add Result\" function now."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        


if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ResultsTrkAddWindow()
    window.show()
    sys.exit(app.exec_())   
      

         
        
        


    
    