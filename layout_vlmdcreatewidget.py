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

class VLMDCreateWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        #self.buttonNewPkg = QtWidgets.QPushButton(text="Create New HEAL-DSC Data Package",parent=self)
        #self.buttonNewPkg.clicked.connect(self.create_new_pkg)

        self.buttonInferHealCsvDd = QtWidgets.QPushButton(text="CSV Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonInferHealCsvDd.clicked.connect(self.csv_data_infer_dd)

        self.buttonSPSSSavExtractHealCsvDd = QtWidgets.QPushButton(text="SPSS Sav Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonSPSSSavExtractHealCsvDd.clicked.connect(self.spss_sav_data_extract_dd)

        self.buttonStataDtaExtractHealCsvDd = QtWidgets.QPushButton(text="Stata Dta Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonStataDtaExtractHealCsvDd.clicked.connect(self.stata_dta_data_extract_dd)

        self.buttonSASSas7bdatExtractHealCsvDd = QtWidgets.QPushButton(text="SAS Sas7bdat Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonSASSas7bdatExtractHealCsvDd.clicked.connect(self.sas_sas7bdat_data_extract_dd)

        self.buttonConvertRedcapCsvDd = QtWidgets.QPushButton(text="Redcap CSV Data Dictionary File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonConvertRedcapCsvDd.clicked.connect(self.redcap_csv_dd_convert)
        
        self.buttonConvertMinimalCsvDd = QtWidgets.QPushButton(text="Minimal CSV Data Dictionary File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonConvertMinimalCsvDd.clicked.connect(self.minimal_csv_dd_convert)
        


        self.buttonConvertExcelMultipleHEALCsvDd = QtWidgets.QPushButton(text="Excel Data Workbook >> HEAL CSV Data Dictionaries (1 DD for every worksheet)",parent=self)
        self.buttonConvertExcelMultipleHEALCsvDd.clicked.connect(lambda exceltype: self.excel_dd_convert("multiple"))
        self.buttonConvertExcelCombinedHEALCsvDd = QtWidgets.QPushButton(text="Excel Data Workbook >> HEAL CSV Data Dictionary (Combined dd of all sheets)",parent=self)
        self.buttonConvertExcelCombinedHEALCsvDd.clicked.connect(lambda exceltype: self.excel_dd_convert("combined"))
        self.buttonConvertExcelFirstHEALCsvDd = QtWidgets.QPushButton(text="Excel Data Workbook >> HEAL CSV Data Dictionary (of first worksheet)",parent=self)
        self.buttonConvertExcelFirstHEALCsvDd.clicked.connect(lambda exceltype: self.excel_dd_convert("first"))
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
        layout.addWidget(self.buttonSPSSSavExtractHealCsvDd)
        layout.addWidget(self.buttonStataDtaExtractHealCsvDd)
        layout.addWidget(self.buttonSASSas7bdatExtractHealCsvDd)
        layout.addWidget(self.buttonConvertRedcapCsvDd)
        layout.addWidget(self.buttonConvertMinimalCsvDd)

        layout.addWidget(self.buttonConvertExcelMultipleHEALCsvDd)
        layout.addWidget(self.buttonConvertExcelCombinedHEALCsvDd)
        layout.addWidget(self.buttonConvertExcelFirstHEALCsvDd)
        
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
            input_filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype="data.csv",
            output_csv_quoting=True
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

    def spss_sav_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input SPSS Sav Data file",
            "FileExplorerOpenFileExt" : "SAV Files (*.sav)",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ",
            "UtilsInputType" : "spss"
        }

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input SPSS Sav Data file",
               (QtCore.QDir.homePath()), "SAV Files (*.sav)")
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = 'Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ' + ifileName
        self.userMessageBox.setText(messageText)

        mydicts = convert_to_vlmd(
            input_filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype="spss",
            output_csv_quoting=True
        )
        
        messageText = messageText + '\n\n\n' + 'Extracted - Success!'
        self.userMessageBox.setText(messageText)

        ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
                       (QtCore.QDir.homePath() + "/" + ifname + ".csv"),"CSV Files (*.csv)") 

        messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.setText(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = messageText + '\n\n\n' + 'Saved - Success!'
        self.userMessageBox.setText(messageText)    
    
    def get_heal_csv_dd(self,get_dd_dict):
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, get_dd_dict["FileExplorerOpenMessage"],
               (QtCore.QDir.homePath()), get_dd_dict["FileExplorerOpenFileExt"])
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = get_dd_dict["GetDDActionStatusMessage"] + ifileName
        self.userMessageBox.setText(messageText)

        mydicts = convert_to_vlmd(
            input_filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype=get_dd_dict["UtilsInputType"],
            output_csv_quoting=True
        )
        
        messageText = messageText + '\n\n\n' + get_dd_dict["GetDDAction"] + ' - Success!'
        self.userMessageBox.setText(messageText)

        ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
                       (QtCore.QDir.homePath() + "/" + ifname + ".csv"),"CSV Files (*.csv)") 

        messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.setText(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = messageText + '\n\n\n' + 'Saved - Success!'
        self.userMessageBox.setText(messageText)

    def stata_dta_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Stata Dta Data file",
            "FileExplorerOpenFileExt" : "DTA Files (*.dta)",
            "GetDDAction": "Extracted",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from Stata Dta data file: ",
            "UtilsInputType" : "dta"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)
        
    def sas_sas7bdat_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input SAS Sas7bdat Data file",
            "FileExplorerOpenFileExt" : "Sas7bdat Files (*.sas7bdat)",
            "GetDDAction": "Extracted",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from SAS Sas7bdat data file: ",
            "UtilsInputType" : "sas"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)
    
    def minimal_csv_dd_convert(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Minimal CSV Data Dictionary file",
            "FileExplorerOpenFileExt" : "CSV (*.csv *.tsv)",
            "GetDDAction": "Converted",
            "GetDDActionStatusMessage" : "Converting the Minimal CSV Data Dictionary at this path to HEAL CSV Data Dictionary: ",
            "UtilsInputType" : "csv-data-dict"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)

    def redcap_csv_dd_convert(self):
        
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input Redcap CSV Data Dictionary file", QtCore.QDir.homePath(), "CSV (*.csv *.tsv)")
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]

        messageText = 'Converting the Redcap CSV Data Dictionary at this path to HEAL CSV Data Dictionary: ' + ifileName 
        self.userMessageBox.setText(messageText)      
       
        #outputFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Output Directory Where HEAL CSV Data Dictionary Should Be Saved!')
        
        mydicts = convert_to_vlmd(
            input_filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype="redcap-csv",
            output_csv_quoting=True
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

    def excel_dd_convert(self,exceltype):
        
        inputmess = "Converting the excel worksheets at this path to a HEAL CSV Data Dictionary ({}):"
        
        if exceltype == "multiple":
            text = "each worksheet -> 1 DD"
            multiple_data_dicts = True
            sheet_name = None
        elif exceltype == "combined":
            text = "combining all worksheets to 1 DD"
            multiple_data_dicts = False
            sheet_name = None
        elif exceltype == "first":
            text = "the first worksheet"
            multiple_data_dicts = False
            sheet_name = 0
        else:
            raise Exception("Need to specify one of: multiple,combined, or first")

        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Excel (xlsx) File",
            "FileExplorerOpenFileExt" : "XLSX (*.xlsx)",
            "GetDDAction": "Converted",
            "GetDDActionStatusMessage" : inputmess.format(text),
            "UtilsInputType" : "excel-data"
        }

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, get_dd_dict["FileExplorerOpenMessage"],
               (QtCore.QDir.homePath()), get_dd_dict["FileExplorerOpenFileExt"])
        
        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = get_dd_dict["GetDDActionStatusMessage"] + ifileName
        self.userMessageBox.setText(messageText)

        mydicts = convert_to_vlmd(
            input_filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype=get_dd_dict["UtilsInputType"],
            output_csv_quoting=True,
            multiple_data_dicts=multiple_data_dicts,
            sheet_name=sheet_name
        )
        
        messageText = messageText + '\n\n\n' + get_dd_dict["GetDDAction"] + ' - Success!'
        self.userMessageBox.setText(messageText)


        if mydicts.get("csvtemplate"):
            mydicts = {"one":mydicts}

        for name,dictionary in mydicts.items():
            ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, f"Save the {name} worksheet to a HEAL CSV Data Dictionary File", 
                        (QtCore.QDir.homePath() + "/" + ifname +"-"+name+"-"+ ".csv"),"CSV Files (*.csv)") 

            messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
            self.userMessageBox.setText(messageText)

            # write just the heal csv dd to file
            pd.DataFrame(dictionary['csvtemplate']).to_csv(ofileName, index = False)

            messageText = messageText + '\n\n\n' + 'Saved - Success!'
            self.userMessageBox.setText(messageText)



    #def show_new_window(self,checked):
    #    if self.w is None:
    #        self.w = CSVEditWindow('')
    #        self.w.show()

    #    else:
    #        self.w.close()  # Close window.
    #        self.w = None  # Discard reference.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VLMDCreateWindow()
    window.show()
    sys.exit(app.exec_())
