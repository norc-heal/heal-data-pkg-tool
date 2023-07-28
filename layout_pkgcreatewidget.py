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

class PkgCreateWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonNewPkg = QtWidgets.QPushButton(text="Create New Data Package",parent=self)
        self.buttonNewPkg.clicked.connect(self.create_new_pkg)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonNewPkg)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_new_pkg(self):
        #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        #folder = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        #filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Hey! Select a File')
        parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Parent Directory Where Data Package Should Be Created!')
        pkgPath = dsc_pkg_utils.new_pkg(pkg_parent_dir_path=parentFolderPath)

        messageText = 'Created new HEAL DSC data package at: ' + pkgPath
        self.userMessageBox.append(messageText)

    