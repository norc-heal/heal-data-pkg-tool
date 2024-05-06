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
import version_update_tracker

import schema_results_tracker
from healdata_utils.validators.jsonschema import validate_against_jsonschema

import pkg_shareable_data

class PkgShareableWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.pkgPath = None # Initialize with no working data package directory path
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        widget = QtWidgets.QWidget()
        
        # self.buttonCheckPkgVersions = QtWidgets.QPushButton(text="Check Package Versions",parent=self)
        # self.buttonCheckPkgVersions.clicked.connect(self.check_pkg_versions)

        self.explainShareablePkg = QtWidgets.QLabel(text = "<b>Prepare your data package for submission to a public data repository by creating a \"shareable\" version of your Data Package.</b><br><br>Your \"Shareable Data Package(s)\" will have the same structure as your study folder, but contain only the study files/resources you intend to share. You can create more than one \"flavor\" of Shareable Data Package. Available \"flavors\" of Shareable Data Package include:<br>1. <b>Open-access, Now</b> - Includes files that have been set as ONLY open-access, and files that have been set as temporary-private and open-access IF the access date is earlier than today's date<br>2. <b>Managed-access, Now</b> - Includes files that have been set as ONLY open-access or ONLY managed-access, and files that have been set as temporary-private AND open-access or managed-access IF the access date is earlier than today's date<br>3. <b>Open-access, By Specified Date</b> - Includes files that have been set as ONLY open-access, and files that have been set as temporary-private and open-access IF the access date is earlier than the user-specified date (usually, a date in the future)<br>4. <b>Managed-access, By Specified Date</b> - Includes files that have been set as ONLY open-access or ONLY managed-access, and files that have been set as temporary-private AND open-access or managed-access IF the access date is earlier than the user-specified date (usually, a date in the future)", parent=self)

        self.dateEdit = QtWidgets.QDateEdit(calendarPopup=True,parent=self)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateEdit.setStyleSheet("background-color: lightgreen") 
        self.labelDateEdit = QtWidgets.QLabel(text = "<b>If creating a flavor of Shareable Data Package that requires a user-specified date, please set the user-specified date here:</b><br>(Click the arrow all the way on the right to pop out a calendar widget)", parent=self)
        self.labelDateEdit.setStyleSheet("background-color: lightgreen") 

        self.buttonOpenAccessNow = QtWidgets.QPushButton(text="Open Access, Now",parent=self)
        self.buttonOpenAccessNow.clicked.connect(self.open_access_now)

        self.buttonManagedAccessNow = QtWidgets.QPushButton(text="Managed Access, Now",parent=self)
        self.buttonManagedAccessNow.clicked.connect(self.managed_access_now) 

        self.buttonOpenAccessByDate = QtWidgets.QPushButton(text="Open Access, By Specified Date",parent=self)
        self.buttonOpenAccessByDate.clicked.connect(self.open_access_by_date)

        self.buttonManagedAccessByDate = QtWidgets.QPushButton(text="Managed Access, By Specified Date",parent=self)
        self.buttonManagedAccessByDate.clicked.connect(self.managed_access_by_date)
        

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)

        self.labelUserMessageBox = QtWidgets.QLabel(text = "User Status Message Box:", parent=self)
        
        layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(self.buttonCheckPkgVersions)
        layout.addWidget(self.explainShareablePkg)
        layout.addWidget(self.labelDateEdit)
        layout.addWidget(self.dateEdit)
        layout.addWidget(self.buttonOpenAccessNow)
        layout.addWidget(self.buttonManagedAccessNow)
        layout.addWidget(self.buttonOpenAccessByDate)
        layout.addWidget(self.buttonManagedAccessByDate)
        layout.addWidget(self.labelUserMessageBox)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_access_now(self):
        print("creating shareable data pkg with flavor: open-access-now")

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return
        
        shareableDir = pkg_shareable_data.createShareableDataPkg(
            workingDataPkgDir=self.workingDataPkgDir,
            flavor="open-access-now"
            )

        print("success")
        messageText = "<br>Success - Your shareable data package was created! This \"open-access-now\" shareable data package contains:<br><br>1. Study files - all study files set as open-access as of today's date<br>2. Standard data package metadata - experiment tracker, resource tracker, and any data dictionary(s) and results tracker(s) that have been set as open-access as of today's date<br><br>You'll find your shareable data package directory at: " + shareableDir + "<br><br>There is also a readme file and an \"overview\" resource tracker with an indicator of which files are shared in this shareable data package at that location. You should:<br><br>1. Inspect your shareable data package, then zip it up once you are satisfied that the correct files have been shared<br>2. Share your zipped up shareable data package directory as open access at your selected data repository<br>3. Share your readme file and \"overview\" resource tracker as open access at your selected data repository<br>"
        errorFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))

    def managed_access_now(self):
        print("creating shareable data pkg with flavor: managed-access-now")

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return
        
        shareableDir = pkg_shareable_data.createShareableDataPkg(
            workingDataPkgDir=self.workingDataPkgDir,
            flavor="managed-access-now"
            )

        print("success")
        messageText = "<br>Success - Your shareable data package was created! This \"managed-access-now\" shareable data package contains:<br><br>1. Study files - all study files set as open-access or managed-access as of today's date<br>2. Standard data package metadata - experiment tracker, resource tracker, and any data dictionary(s) and results tracker(s) that have been set as open-access or managed-access as of today's date<br><br>You'll find your shareable data package directory at: " + shareableDir + "<br><br>There is also a readme file and an \"overview\" resource tracker with an indicator of which files are shared in this shareable data package at that location. You should:<br><br>1. Inspect your shareable data package, then zip it up once you are satisfied that the correct files have been shared<br>2. Share your zipped up shareable data package directory as managed access at your selected data repository<br>3. Share your readme file and \"overview\" resource tracker as open access at your selected data repository<br>"
        errorFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
        
    def open_access_by_date(self):
        print("creating shareable data pkg with flavor: open-access-by-date")

        byDate = self.dateEdit.date().toString("MM/dd/yyyy")

        print("byDate: ",byDate)

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return
        
        shareableDir = pkg_shareable_data.createShareableDataPkg(
            workingDataPkgDir=self.workingDataPkgDir,
            flavor="open-access-by-date",
            byDate=byDate
            ) 

        print("success") 
        messageText = "<br>Success - Your shareable data package was created! This \"open-access-by-date\" shareable data package contains:<br><br>1. Study files - all study files set as open-access as of " + byDate + "<br>2. Standard data package metadata - experiment tracker, resource tracker, and any data dictionary(s) and results tracker(s) that have been set as open-access as of " + byDate + "<br><br>You'll find your shareable data package directory at: " + shareableDir + "<br><br>There is also a readme file and an \"overview\" resource tracker with an indicator of which files are shared in this shareable data package at that location. You should:<br><br>1. Inspect your shareable data package, then zip it up once you are satisfied that the correct files have been shared<br>2. Share your zipped up shareable data package directory as open access but under embargo until " + byDate + " at your selected data repository<br>3. Share your readme file and \"overview\" resource tracker as open access at your selected data repository<br>"
        errorFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))  
   
    def managed_access_by_date(self):
        print("creating shareable data pkg with flavor: managed-access-by-date")

        byDate = self.dateEdit.date().toString("MM/dd/yyyy")

        print("byDate: ",byDate)

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return
        
        shareableDir = pkg_shareable_data.createShareableDataPkg(
            workingDataPkgDir=self.workingDataPkgDir,
            flavor="managed-access-by-date",
            byDate=byDate
            ) 

        print("success") 
        messageText = "<br>Success - Your shareable data package was created! This \"managed-access-by-date\" shareable data package contains:<br><br>1. Study files - all study files set as open-access or managed-access as of " + byDate + "<br>2. Standard data package metadata - experiment tracker, resource tracker, and any data dictionary(s) and results tracker(s) that have been set as open-access or managed-access as of " + byDate + "<br><br>You'll find your shareable data package directory at: " + shareableDir + "<br><br>There is also a readme file and an \"overview\" resource tracker with an indicator of which files are shared in this shareable data package at that location. You should:<br><br>1. Inspect your shareable data package, then zip it up once you are satisfied that the correct files have been shared<br>2. Share your zipped up shareable data package directory as managed access but under embargo until " + byDate + " at your selected data repository<br>3. Share your readme file and \"overview\" resource tracker as open access at your selected data repository<br>"
        errorFormat = '<span style="color:green;">{}</span>' 
        self.userMessageBox.append(errorFormat.format(messageText))    
   
    