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

import version_check

class PkgCreateWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.pkgPath = None # Initialize with no working data package directory path
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        widget = QtWidgets.QWidget()
        
        self.buttonNewPkg = QtWidgets.QPushButton(text="Create New Data Package",parent=self)
        self.buttonNewPkg.clicked.connect(self.create_new_pkg)

        self.buttonContinuePkg = QtWidgets.QPushButton(text="Continue Existing Data Package",parent=self)
        self.buttonContinuePkg.clicked.connect(self.continue_pkg)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonNewPkg)
        layout.addWidget(self.buttonContinuePkg)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_new_pkg(self):
        
        parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Parent Directory Where Data Package Directory Should Be Created!')
        
        if not parentFolderPath:
            messageText = "<br>" + "You must select a parent directory where the Data Package Directory should be created to proceed."
            self.userMessageBox.append(messageText)
            return

        pkgPath = dsc_pkg_utils.new_pkg(pkg_parent_dir_path=parentFolderPath)

        if not pkgPath:
            messageText = "<br>" + "A Data Package Directory could not be created at " + parentFolderPath + ". Check to see if a Data Package Directory (i.e. a directory called \"dsc-pkg\") already exists at this location."
            self.userMessageBox.append(messageText)
            return

        messageText = "<br>" + "Created new HEAL DSC Data Package Directory at: "  + pkgPath
        self.userMessageBox.append(messageText)

        messageText = "<br>" + "Your working Data Package Directory has been set at: "  + pkgPath
        self.userMessageBox.append(messageText)

        self.pkgPath = pkgPath
        self.workingDataPkgDirDisplay.setText(self.pkgPath)
        

    def continue_pkg(self):
        
        pkgPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Existing Data Package Directory!')
        
        if not pkgPath:
            messageText = "<br>" + "You must select an existing Data Package Directory to proceed."
            self.userMessageBox.append(messageText)
            return

        requiredFiles = ["heal-csv-experiment-tracker.csv","heal-csv-resource-tracker.csv"]
        requiredDirPrefix = "dsc-pkg"

        print(Path(pkgPath).name)
        print(str(Path(pkgPath).name))
        print(str(Path(pkgPath).name).startswith(requiredDirPrefix))

        if not str(Path(pkgPath).name).startswith(requiredDirPrefix):
            messageText = "<br>" + "The directory you selected as your existing Data Package Directory does not have a name that starts with the required Data Package Directory prefix of " + requiredDirPrefix + ". Check that you selected the correct directory. You can use the Create New Data Package push button above to create a new Data Package Directory with the required Data Package Directory prefix."
            self.userMessageBox.append(messageText)
            return

        requiredFilesExist = [os.path.isfile(os.path.join(pkgPath,f)) for f in requiredFiles]
        print("requiredFilesExist: ", requiredFilesExist)

        if not all(requiredFilesExist):
            messageText = "<br>" + "The directory you selected as your existing Data Package Directory does not contain all required files for an initialized Data Package Directory. Required files include: " + "<br><br>" + "<br>".join(requiredFiles) + "<br><br>" + "Check that you selected the correct directory. You can use the Create New Data Package push button above to create a new Data Package Directory with the required files." 
            self.userMessageBox.append(messageText)
            return

        messageText = "<br>" + "Your working Data Package Directory has been set at: "  + pkgPath + "<br><br>Checking if updates to dsc-pkg files are needed...<br>"
        self.userMessageBox.append(messageText)
        QApplication.processEvents() # print accumulated user status messages

        self.pkgPath = pkgPath
        self.workingDataPkgDirDisplay.setText(self.pkgPath)

        versionCheck = version_check.version_check(self.pkgPath)
        
        versionCheckAllUpToDate = versionCheck[0]
        versionCheckMessageText = versionCheck[1]

        messageText = "<br>" + versionCheckMessageText
        
        if versionCheckAllUpToDate:
            saveFormat = '<span style="color:green;">{}</span>'
        else:
            saveFormat = '<span style="color:red;">{}</span>'

        self.userMessageBox.append(saveFormat.format(messageText)) 

    