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
#from layout_csveditwidget import CSVEditWindow
from layout_csvviewwidget import CSVViewWindow

class CSVViewPushToLoadWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay, fileBaseName, fileStartsWith, fileTypeTitle):
        super().__init__()
        self.w = None  # No external window yet.
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.fileBaseName = fileBaseName
        self.fileStartsWith = fileStartsWith
        self.fileTypeTitle = fileTypeTitle
        
        widget = QtWidgets.QWidget()
        
        self.buttonViewCsv = QtWidgets.QPushButton(text="View CSV", parent=self)
        self.buttonViewCsv.clicked.connect(self.view_csv)
        

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonViewCsv)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def view_csv(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        if self.fileBaseName:
            self.fileName = os.path.join(self.workingDataPkgDir,self.fileBaseName)
        else:
            self.fileName = self.workingDataPkgDir

        if self.w is None:
            self.w = CSVViewWindow(fileName=self.fileName,fileStartsWith=self.fileStartsWith,fileTypeTitle=self.fileTypeTitle)
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = CSVViewPushToLoadWindow()
    window.show()
    sys.exit(app.exec_())