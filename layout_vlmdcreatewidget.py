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
from layout_csveditwidget import CSVEditWindow

class VLMDCreateWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        #self.buttonNewPkg = QtWidgets.QPushButton(text="Create New HEAL-DSC Data Package",parent=self)
        #self.buttonNewPkg.clicked.connect(self.create_new_pkg)

        self.buttonInferHealCsvDd = QtWidgets.QPushButton(text="CSV Data >> HEAL CSV Data Dictionary",parent=self)
        self.buttonInferHealCsvDd.clicked.connect(self.csv_data_infer_dd)

        self.buttonConvertRedcapCsvDd = QtWidgets.QPushButton(text="Redcap CSV Data Dictionary >> HEAL CSV Data Dictionary",parent=self)
        self.buttonConvertRedcapCsvDd.clicked.connect(self.redcap_csv_dd_convert)
        #self.buttonConvertRedcapCsvDd.setFixedSize(100,60)

        #self.buttonEditCsv = QtWidgets.QPushButton(text="View/Edit CSV", parent=self)
        #self.buttonEditCsv.clicked.connect(self.show_new_window)
        #self.setCentralWidget(self.buttonEditCsv)
        #self.buttonEditCsv.setFixedSize(100,60)

        #self.buttonValidateHealCsvDd = QtWidgets.QPushButton(text="Validate HEAL CSV Data Dictionary", parent=self)
        #self.buttonValidateHealCsvDd.setFixedSize(100,60)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(self.buttonNewPkg)
        layout.addWidget(self.buttonInferHealCsvDd)
        layout.addWidget(self.buttonConvertRedcapCsvDd)
        #layout.addWidget(self.buttonEditCsv)
        #layout.addWidget(self.buttonValidateHealCsvDd)
        layout.addWidget(self.userMessageBox)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    #def create_new_pkg(self):
    #    #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
    #    #folder = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
    #    #filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Hey! Select a File')
    #    parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Parent Directory Where Data Package Should Be Created!')
    #    pkgPath = dsc_pkg_utils.new_pkg(pkg_parent_dir_path=parentFolderPath)

    #    messageText = 'Created new HEAL DSC data package at: ' + pkgPath
    #    self.userMessageBox.setText(messageText)

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