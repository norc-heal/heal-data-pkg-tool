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
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Input Resource Txt Data file",
               (QtCore.QDir.homePath()), "Text (*.txt)")
        
        # load resource file and convert to python object
        path = ifileName
        data = json.loads(Path(path).read_text())
        print(data)

        # validate experiment file json content against experiment tracker json schema
        out = validate_against_jsonschema(data, schema_resource_tracker)
        print(out["valid"])
        print(out["errors"])

        # print validation errors and exit if not valid
        if out["valid"]:
            messageText = "The following resource file is valid: " + ifileName
            self.userMessageBox.setText(messageText)
        else:
            messageText = "The following resource file is NOT valid and will not be added to your Resource Tracker file: " + ifileName + "\n\n\n" + "Validation errors are as follows: " + out["errors"] + "\n\n\n" + "Exiting \"Add Resource\" function now."
            self.userMessageBox.setText(messageText)
            return
        
        # if valid, convert json to pd
        df = pd.json_normalize(data)
        print(df)

        # get data package directory path
        parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Resource Tracker File lives here!')
        
        # check if resource tracker file exists
        # if exists, append the pd data object from the experiment file as a new row in the experiment tracker file
        # if doesn't exist, print error/info message and exit
        if "heal-csv-resource-tracker.csv" in os.listdir(parentFolderPath):
            
            output_path=os.path.join(parentFolderPath,"heal-csv-resource-tracker.csv")
            all_df = pd.read_csv(output_path)
            all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
            # before writing to file may want to check for duplicate resource IDs and if duplicate resource IDs, ensure that 
            # user wants to overwrite the earlier instance of the resource ID in the resource tracker

            all_df.to_csv(output_path, mode='w', header=True, index=False)
            #df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

            messageText = messageText + "\n\n\n" + "The contents of the Resource file: " + "\n\n\n" + ifileName + "\n\n\n" + "were added as a resource to the Resource Tracker file: " + "\n\n\n" + output_path
            self.userMessageBox.setText(messageText)
        else:
            messageText = messageText + "\n\n\n" + "No Resource Tracker file exists at the designated directory. Are you sure this is a Data Package Directory? If you haven't yet created a Data Package Directory for your work, please head to the \"Data Package\" tab and use the \"Create new Data Package\" button to create your Data Package Directory. Your new Data Package Directory will contain your Resource Tracker file. You can then come back here and try adding your resource file again!" + "\n\n\n" + "Exiting \"Add Resource\" function now."
            self.userMessageBox.setText(messageText)
            return
        
        
        
      

         
        
        


    
    