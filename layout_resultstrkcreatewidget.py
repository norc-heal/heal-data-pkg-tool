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

class ResultsTrkCreateWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonNewResultsTrk = QtWidgets.QPushButton(text="Create New Results Tracker",parent=self)
        self.buttonNewResultsTrk.clicked.connect(self.create_new_results_trk)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonNewResultsTrk)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_new_results_trk(self):
                 
        resultsTrkDirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory Where Results Tracker Should Be Created!")
        
        if resultsTrkDirPath:
            df, fName = dsc_pkg_utils.new_results_trk()

            #ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save your HEAL formatted Result Tracker File!", 
            #           (QtCore.QDir.homePath() + "/" + fName),"CSV Files (*.csv)") 

            ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save your HEAL formatted Result Tracker File!", 
                       os.path.join(resultsTrkDirPath,fName),"CSV Files (*.csv)") 
            
            if ofileName:
                df.to_csv(ofileName, index = False) 

                messageText = 'Created new HEAL formatted Results Tracker at: ' + ofileName
                self.userMessageBox.append(messageText)
            
            else:
                messageText = "<br>You have not added a filename and location with/at which to save your result tracker. Please specify a filename and location for saving your result tracker."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
                return

        else:
            messageText = "<br>You have not selected a directory in which to create the result tracker. Please select a directory."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

    