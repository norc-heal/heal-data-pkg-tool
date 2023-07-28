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
import pipe

import dsc_pkg_utils # local module, no pip install needed

class InfoTextWindow(QtWidgets.QMainWindow):

    def __init__(self, infoText):
        super().__init__()
        self.w = None  # No external window yet.
        self.infoText = infoText
        
        widget = QtWidgets.QWidget()
        
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        #messageText = "You should create a data dictionary for every tabular or tabular-like data file you collect/share as part of your study. This allows you to memorialize what each variable in your dataset is/represents, what values it can take on, etc. This will facilitate continuity and passed-down knowledge within study groups, and sharing and re-use of the data outside of the original study group."
        messageText = self.infoText
        self.userMessageBox.setText(messageText)

    
    