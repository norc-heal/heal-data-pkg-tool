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
from layout_scrollannotateresourcewidget import ScrollAnnotateResourceWindow

import jsonschema
from jsonschema import validate
from schema_resource_tracker import schema_resource_tracker

from healdata_utils.validators.jsonschema import validate_against_jsonschema
import datetime


class ResourceTrkAddWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonAnnotateResource = QtWidgets.QPushButton(text="Annotate a new resource",parent=self)
        self.buttonAnnotateResource.clicked.connect(self.annotate_resource)

        self.buttonAddResource = QtWidgets.QPushButton(text="Add resource to tracker",parent=self)
        self.buttonAddResource.clicked.connect(self.add_resource)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        
        layout.addWidget(self.buttonAnnotateResource)
        layout.addWidget(self.buttonAddResource)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def annotate_resource(self,checked):
        if self.w is None:
            self.w = ScrollAnnotateResourceWindow()
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def add_resource(self):

        # get resource file path
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Resource Txt Data file(s)",
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

                # validate experiment file json content against experiment tracker json schema
                out = validate_against_jsonschema(data, schema_resource_tracker)
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

                    add_to_df_dict = {#"resource.id":[resource_id],
                                    "resource.id.num": [int(resIdNumStr)],  
                                    "resource.create.date.time": [res_c_datetime],
                                    "resource.mod.date.time": [res_m_datetime],
                                    "resource.mod.time.stamp": [res_m_timestamp],
                                    "restrk.create.date.time": [restrk_c_datetime],
                                    "restrk.mod.date.time": [restrk_m_datetime],
                                    "restrk.mod.time.stamp": [restrk_m_timestamp]}

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

        # get data package directory path
        parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Resource Tracker File lives here!')
        
        # check if resource tracker file exists
        # if exists, append the pd data object from the experiment file as a new row in the experiment tracker file
        # if doesn't exist, print error/info message and exit
        if "heal-csv-resource-tracker.csv" in os.listdir(parentFolderPath):
            
            output_path=os.path.join(parentFolderPath,"heal-csv-resource-tracker.csv")
            all_df = pd.read_csv(output_path)
            #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            all_df = pd.concat([all_df, collect_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
            all_df.sort_values(by = ["resource.id.num", "restrk.mod.time.stamp"], inplace=True)
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
      

         
        
        


    
    