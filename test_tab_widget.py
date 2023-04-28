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

###

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
)

from layout_colorwidget import Color
#from layout_vlmdwidget import VLMDWindow
from layout_vlmdtabswidget import VLMDTabsWindow
#from layout_vlmdcreatewidget import VLMDCreateWindow
from layout_csveditwidget import CSVEditWindow

# this will prevent windows from setting the app icon to python automatically based on .py suffix
try:
    from ctypes import windll # only exists on windows, base python, no pip install needed
    myappid = 'mycompany.myproduct.subproduct.version' # somewhat arbitrary string, can set this to the recommendation but not really necessary
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

basedir = os.path.dirname(__file__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DSC Data Packaging Tool - alpha")

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tabs.setMovable(True)

        tabs.addTab(VLMDTabsWindow(), "Data Dictionary")
        for n, color in enumerate(["red", "green", "blue", "yellow"]):
            tabs.addTab(Color(color), color)

        
        self.setCentralWidget(tabs)


#app = QApplication(sys.argv)

#window = MainWindow()
#window.show()

#app.exec()

if __name__ == "__main__":
   import sys
 
   app = QtWidgets.QApplication(sys.argv)
   app.setWindowIcon(QtGui.QIcon(os.path.join(basedir,'heal-icon.ico')))
   #app.setApplicationName('DSC Data Packaging Tool - alpha')
   
   w = MainWindow()
   w.show()
   
   #main = MyWindow('')
   #main.setMinimumSize(820, 300)
   #main.setGeometry(0,0,820,700)
   #main.setWindowTitle("CSV Viewer")
   #main.show()
 
sys.exit(app.exec_())