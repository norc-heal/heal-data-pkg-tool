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

import jsonschema
from jsonschema import validate
from schema_experiment_tracker import schema_experiment_tracker

class ExpTrkAddWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonAnnotateExp = QtWidgets.QPushButton(text="Annotate a new experiment",parent=self)
        self.buttonAnnotateExp.clicked.connect(self.annotate_exp)

        self.buttonAddExp = QtWidgets.QPushButton(text="Add experiment to tracker",parent=self)
        self.buttonAddExp.clicked.connect(self.add_exp)

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

    def add_exp(self):

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Input Experiment Txt Data file",
               (QtCore.QDir.homePath()), "Text (*.txt)")
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]

        # load experiment file - txt file with json data and convert json to python object
        data =[]
        with open(ifileName) as f:
            data = json.load(f)
        print(data)
        body_json = json.dumps(data)
        print(body_json)
            
            #for line in f:
            #    data = json.loads(line)
            #    print(data)
            #    body_json=json.dumps(data)
            #    print(body_json)

        # validate against experiment tracker schema
        print(schema_experiment_tracker)
        isValid = dsc_pkg_utils.validateJson(body_json, schema_experiment_tracker)
        
        if isValid:
            print("Given JSON data is Valid")
        else:
            print("Given JSON data is InValid")

         
        
        #messageText = 'Inferring minimal data dictionary from tabular csv data file: ' + ifileName
        #self.userMessageBox.setText(messageText)


    
    