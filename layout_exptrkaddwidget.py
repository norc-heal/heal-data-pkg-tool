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
from layout_annotateexpwidget import AnnotateExpWindow

class ExpTrkAddWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonAnnotateExp = QtWidgets.QPushButton(text="Annotate a new experiment",parent=self)
        self.buttonAnnotateExp.clicked.connect(self.annotate_exp)

        self.buttonAddExp = QtWidgets.QPushButton(text="Add experiment to tracker",parent=self)
        #self.buttonAddExp.clicked.connect(self.add_exp)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        
        layout.addWidget(self.buttonAnnotateExp)
        layout.addWidget(self.buttonAddExp)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def annotate_exp(self,checked):
        if self.w is None:
            self.w = AnnotateExpWindow()
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
    
    def csv_data_infer_dd(self):
        
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input Tabular CSV Data file",
               (QtCore.QDir.homePath()), "CSV (*.csv *.tsv)")
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = 'Inferring minimal data dictionary from tabular csv data file: ' + ifileName
        self.userMessageBox.setText(messageText)

        mydicts = convert_to_vlmd(
            filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype="data.csv"
        )
        
        messageText = messageText + '\n\n\n' + 'Inferred - Success!'
        self.userMessageBox.setText(messageText)

        ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
                       (QtCore.QDir.homePath() + "/" + ifname + ".csv"),"CSV Files (*.csv)") 

        messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.setText(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = messageText + '\n\n\n' + 'Saved - Success!'
        self.userMessageBox.setText(messageText)

    def spss_sav_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input SPSS Sav Data file",
            "FileExplorerOpenFileExt" : "SAV Files (*.sav)",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ",
            "UtilsInputType" : "sav"
        }

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input SPSS Sav Data file",
               (QtCore.QDir.homePath()), "SAV Files (*.sav)")
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = 'Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ' + ifileName
        self.userMessageBox.setText(messageText)

        mydicts = convert_to_vlmd(
            filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype="sav"
        )
        
        messageText = messageText + '\n\n\n' + 'Extracted - Success!'
        self.userMessageBox.setText(messageText)

        ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
                       (QtCore.QDir.homePath() + "/" + ifname + ".csv"),"CSV Files (*.csv)") 

        messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.setText(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = messageText + '\n\n\n' + 'Saved - Success!'
        self.userMessageBox.setText(messageText)    
    
    def get_heal_csv_dd(self,get_dd_dict):
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, get_dd_dict["FileExplorerOpenMessage"],
               (QtCore.QDir.homePath()), get_dd_dict["FileExplorerOpenFileExt"])
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = get_dd_dict["GetDDActionStatusMessage"] + ifileName
        self.userMessageBox.setText(messageText)

        mydicts = convert_to_vlmd(
            filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype=get_dd_dict["UtilsInputType"]
        )
        
        messageText = messageText + '\n\n\n' + get_dd_dict["GetDDAction"] + ' - Success!'
        self.userMessageBox.setText(messageText)

        ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
                       (QtCore.QDir.homePath() + "/" + ifname + ".csv"),"CSV Files (*.csv)") 

        messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.setText(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = messageText + '\n\n\n' + 'Saved - Success!'
        self.userMessageBox.setText(messageText)

    def stata_dta_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Stata Dta Data file",
            "FileExplorerOpenFileExt" : "DTA Files (*.dta)",
            "GetDDAction": "Extracted",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from Stata Dta data file: ",
            "UtilsInputType" : "dta"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)
        
    def sas_sas7bdat_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input SAS Sas7bdat Data file",
            "FileExplorerOpenFileExt" : "Sas7bdat Files (*.sas7bdat)",
            "GetDDAction": "Extracted",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from SAS Sas7bdat data file: ",
            "UtilsInputType" : "sas7bdat"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)
    
    def redcap_csv_dd_convert(self):
        
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input Redcap CSV Data Dictionary file", QtCore.QDir.homePath(), "CSV (*.csv *.tsv)")
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]

        messageText = 'Converting the Redcap CSV Data Dictionary at this path to HEAL CSV Data Dictionary: ' + ifileName 
        self.userMessageBox.setText(messageText)      
       
        #outputFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Output Directory Where HEAL CSV Data Dictionary Should Be Saved!')
        
        mydicts = convert_to_vlmd(
            filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype="redcap.csv"
        )

        messageText = messageText + '\n\n\n' + 'Converted - Success!'
        self.userMessageBox.setText(messageText)

        ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
                       (QtCore.QDir.homePath() + "/" + ifname + ".csv"),"CSV Files (*.csv)") 

        messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.setText(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = messageText + '\n\n\n' + 'Saved - Success!'
        self.userMessageBox.setText(messageText) 


    #def show_new_window(self,checked):
    #    if self.w is None:
    #        self.w = CSVEditWindow('')
    #        self.w.show()

    #    else:
    #        self.w.close()  # Close window.
    #        self.w = None  # Discard reference.