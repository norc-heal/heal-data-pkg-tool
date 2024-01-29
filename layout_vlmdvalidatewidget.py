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
from healdata_utils import validate_vlmd_csv

#from frictionless import plugins # frictionless already installed as a healdata_utils dependency, no pip install needed
#from frictionless.plugins import remote
#from frictionless import describe

import pandas as pd # pandas already installed as a healdata_utils dependency, no pip install needed
import json # base python, no pip install needed
import pipe

import dsc_pkg_utils # local module, no pip install needed

class VLMDValidateWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonValidateHealCsvDd = QtWidgets.QPushButton(text="Validate HEAL CSV Data Dictionary", parent=self)
        self.buttonValidateHealCsvDd.clicked.connect(self.validate_heal_csv_dd)
        
        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonValidateHealCsvDd)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def validate_heal_csv_dd(self):


        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Select the HEAL CSV data dictionary to validate",
            QtCore.QDir.homePath(), "CSV (*.csv *.tsv)")

        messageText = 'Validating the HEAL CSV Data Dictionary at this path: ' + ifileName 
        self.userMessageBox.setText(messageText)
        
        dd_package = validate_vlmd_csv(ifileName, to_sync_fields=True)
        report = dd_package["report"]

        messageText += "\n\n\n"
        if report["valid"]:  
            messageText +=  "Your data dictionary is valid!"
        else:
            messageText += "Your data dictionary requires the following additional annotation and/or modifications to be HEAL-compliant:"
            messageText += "\n\n\n"
            report_text = json.dumps(report["errors"], indent=4)  
            messageText +=  report_text
            
        self.userMessageBox.setText(messageText)