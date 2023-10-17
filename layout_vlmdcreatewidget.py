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
from healdata_utils.conversion import input_short_descriptions

#from frictionless import plugins # frictionless already installed as a healdata_utils dependency, no pip install needed
#from frictionless.plugins import remote
#from frictionless import describe

import pandas as pd # pandas already installed as a healdata_utils dependency, no pip install needed
import json # base python, no pip install needed
import pipe

import dsc_pkg_utils # local module, no pip install needed
from layout_csveditwidget import CSVEditWindow

class VLMDCreateWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.w = None  # No external window yet.
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        widget = QtWidgets.QWidget()
        
        #self.buttonNewPkg = QtWidgets.QPushButton(text="Create New HEAL-DSC Data Package",parent=self)
        #self.buttonNewPkg.clicked.connect(self.create_new_pkg)

        self.buttonCsvDataInferHealCsvDd = QtWidgets.QPushButton(text="CSV Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonCsvDataInferHealCsvDd.clicked.connect(self.csv_data_infer_dd)
        self.buttonCsvDataInferHealCsvDd.setToolTip(input_short_descriptions["csv-data"])

        self.buttonXlsxDataInferMultipleHealCsvDd = QtWidgets.QPushButton(text="Excel Data File >> HEAL CSV Data Dictionary (one per tab)",parent=self)
        self.buttonXlsxDataInferMultipleHealCsvDd.clicked.connect(lambda exceltype: self.xlsx_data_infer_dd("multiple"))
        self.buttonXlsxDataInferMultipleHealCsvDd.setToolTip(input_short_descriptions["excel-data"])

        self.buttonXlsxDataInferCombinedHealCsvDd = QtWidgets.QPushButton(text="Excel Data File >> HEAL CSV Data Dictionary (one across tabs)",parent=self)
        self.buttonXlsxDataInferCombinedHealCsvDd.clicked.connect(lambda exceltype: self.xlsx_data_infer_dd("combined"))
        self.buttonXlsxDataInferCombinedHealCsvDd.setToolTip(input_short_descriptions["excel-data"])

        self.buttonSPSSSavExtractHealCsvDd = QtWidgets.QPushButton(text="SPSS Sav Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonSPSSSavExtractHealCsvDd.clicked.connect(self.spss_sav_data_extract_dd)
        self.buttonSPSSSavExtractHealCsvDd.setToolTip(input_short_descriptions["spss"])

        self.buttonStataDtaExtractHealCsvDd = QtWidgets.QPushButton(text="Stata Dta Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonStataDtaExtractHealCsvDd.clicked.connect(self.stata_dta_data_extract_dd)
        self.buttonStataDtaExtractHealCsvDd.setToolTip(input_short_descriptions["stata"])

        self.buttonSASSas7bdatExtractHealCsvDd = QtWidgets.QPushButton(text="SAS Sas7bdat Data File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonSASSas7bdatExtractHealCsvDd.clicked.connect(self.sas_sas7bdat_data_extract_dd)
        self.buttonSASSas7bdatExtractHealCsvDd.setToolTip(input_short_descriptions["sas"])

        self.buttonConvertRedcapCsvDd = QtWidgets.QPushButton(text="Redcap CSV Data Dictionary File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonConvertRedcapCsvDd.clicked.connect(self.redcap_csv_dd_convert)
        self.buttonConvertRedcapCsvDd.setToolTip(input_short_descriptions["redcap-csv"])
        
        self.buttonConvertMinimalCsvDd = QtWidgets.QPushButton(text="Minimal CSV Data Dictionary File >> HEAL CSV Data Dictionary",parent=self)
        self.buttonConvertMinimalCsvDd.clicked.connect(self.minimal_csv_dd_convert)
        self.buttonConvertMinimalCsvDd.setToolTip(input_short_descriptions["csv-data-dict"])
        


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
        
        self.layout = QtWidgets.QVBoxLayout()

        self.data_input_layout = QtWidgets.QVBoxLayout()
        self.dd_input_layout = QtWidgets.QVBoxLayout()

        
        self.data_input_layout.addWidget(self.buttonCsvDataInferHealCsvDd)
        self.data_input_layout.addWidget(self.buttonXlsxDataInferMultipleHealCsvDd)
        self.data_input_layout.addWidget(self.buttonXlsxDataInferCombinedHealCsvDd)

        self.data_input_layout.addWidget(self.buttonSPSSSavExtractHealCsvDd)
        self.data_input_layout.addWidget(self.buttonStataDtaExtractHealCsvDd)
        self.data_input_layout.addWidget(self.buttonSASSas7bdatExtractHealCsvDd)

        self.dd_input_layout.addWidget(self.buttonConvertMinimalCsvDd)
        self.dd_input_layout.addWidget(self.buttonConvertRedcapCsvDd)

        self.data_input_groupbox = QtWidgets.QGroupBox("Start with a Data File")
        self.data_input_groupbox.setLayout(self.data_input_layout)

        self.dd_input_groupbox = QtWidgets.QGroupBox("Start with a Data Dictionary File")
        self.dd_input_groupbox.setLayout(self.dd_input_layout)


        # layout.addWidget(self.buttonInferHealCsvDd)
        # layout.addWidget(self.buttonSPSSSavExtractHealCsvDd)
        # layout.addWidget(self.buttonStataDtaExtractHealCsvDd)
        # layout.addWidget(self.buttonSASSas7bdatExtractHealCsvDd)
        # layout.addWidget(self.buttonConvertRedcapCsvDd)
        # layout.addWidget(self.buttonConvertMinimalCsvDd)

        # layout.addWidget(self.buttonConvertExcelMultipleHEALCsvDd)
        # layout.addWidget(self.buttonConvertExcelCombinedHEALCsvDd)
       
        self.layout.addWidget(self.data_input_groupbox)
        self.layout.addWidget(self.dd_input_groupbox)

        self.layout.addWidget(self.userMessageBox)

        
        
        widget.setLayout(self.layout)
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

        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input CSV Data file",
            "FileExplorerOpenFileExt" : "CSV (*.csv *.tsv)",
            "GetDDAction": "Inferred",
            "GetDDActionStatusMessage" : "Inferring minimal HEAL CSV Data Dictionary from CSV data file: ",
            "UtilsInputType" : "csv-data"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)

        ###

        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input Tabular CSV Data file",
        #        (QtCore.QDir.homePath()), "CSV (*.csv *.tsv)")
        
        # ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        # messageText = 'Inferring minimal HEAL CSV Data Dictionary from tabular csv data file: ' + ifileName
        # self.userMessageBox.setText(messageText)

        # mydicts = convert_to_vlmd(
        #     input_filepath=ifileName,
        #     data_dictionary_props={
        #         "title":"my dd title",
        #         "description":"my dd description"
        #     },
        #     inputtype="csv-data",
        #     output_csv_quoting=True
        # )
        
        # messageText = messageText + '\n\n\n' + 'Inferred - Success!'
        # self.userMessageBox.setText(messageText)

        # ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
        #                (QtCore.QDir.homePath() + "/" + "heal-csv-dd-" + ifname + ".csv"),"CSV Files (*.csv)") 

        # messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        # self.userMessageBox.setText(messageText)

        # # write just the heal csv dd to file
        # pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        # messageText = messageText + '\n\n\n' + 'Saved - Success!'
        # self.userMessageBox.setText(messageText)

    def spss_sav_data_extract_dd(self):

        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input SPSS Sav Data file",
            "FileExplorerOpenFileExt" : "SAV Files (*.sav)",
            "GetDDAction": "Extracted",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ",
            "UtilsInputType" : "spss"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)

        ###
        
        # get_dd_dict = {
        #     "FileExplorerOpenMessage" : "Select Input SPSS Sav Data file",
        #     "FileExplorerOpenFileExt" : "SAV Files (*.sav)",
        #     "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ",
        #     "UtilsInputType" : "spss"
        # }

        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input SPSS Sav Data file",
        #        (QtCore.QDir.homePath()), "SAV Files (*.sav)")
        
        # ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        # messageText = 'Extracting metadata to populate HEAL CSV Data Dictionary from SPSS Sav data file: ' + ifileName
        # self.userMessageBox.setText(messageText)

        # mydicts = convert_to_vlmd(
        #     input_filepath=ifileName,
        #     data_dictionary_props={
        #         "title":"my dd title",
        #         "description":"my dd description"
        #     },
        #     inputtype="spss",
        #     output_csv_quoting=True
        # )
        
        # messageText = messageText + '\n\n\n' + 'Extracted - Success!'
        # self.userMessageBox.setText(messageText)

        # ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
        #                (QtCore.QDir.homePath() + "/" + "heal-csv-dd-" + ifname + ".csv"),"CSV Files (*.csv)") 

        # messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        # self.userMessageBox.setText(messageText)

        # # write just the heal csv dd to file
        # pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        # messageText = messageText + '\n\n\n' + 'Saved - Success!'
        # self.userMessageBox.setText(messageText)    
    
    def get_heal_csv_dd(self,get_dd_dict):
        
        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        print("workingDataPkgDir: ", self.workingDataPkgDir)

        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, get_dd_dict["FileExplorerOpenMessage"],
        #        (QtCore.QDir.homePath()), get_dd_dict["FileExplorerOpenFileExt"])

        # this will open file browser in the working data pkg dir - while the file they are looking for
        # should not be in the working data pkg dir, if user followed best practices and placed their 
        # working data pkg dir as a direct sub-dir of their overall study folder, then they will be one level
        # down into their overall study folder and this should be a good starting point from which to browse
        # to the data or dd file they are looking for as the starting point for creating their heal csv dd
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, get_dd_dict["FileExplorerOpenMessage"],
               self.workingDataPkgDir, get_dd_dict["FileExplorerOpenFileExt"])

        # error handling for if user does not select a file
        if not ifileName:
            messageText = "<br><br>" + "You did not select a file - To proceed, you must: " + get_dd_dict["FileExplorerOpenMessage"] + "<br><br>"
            self.userMessageBox.append(messageText)

        ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]
        
        messageText = get_dd_dict["GetDDActionStatusMessage"] + ifileName
        self.userMessageBox.append(messageText)

        mydicts = convert_to_vlmd(
            input_filepath=ifileName,
            data_dictionary_props={
                "title":"my dd title",
                "description":"my dd description"
            },
            inputtype=get_dd_dict["UtilsInputType"],
            output_csv_quoting=True
        )
        
        messageText = "<br><br>" + get_dd_dict["GetDDAction"] + ' - Success!'
        self.userMessageBox.append(messageText)

        # ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
        #                (QtCore.QDir.homePath() + "/" + "heal-csv-dd-" + ifname + ".csv"),"CSV Files (*.csv)")

        # by default, save in working data pkg dir with prefix of heal-csv-dd appended to 
        # originating data/dd file name
        ofileNameBase = "heal-csv-dd-" + ifname + ".csv"
        ofileName = os.path.join(self.workingDataPkgDir, ofileNameBase) 

        messageText = "<br><br>" + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        self.userMessageBox.append(messageText)

        # write just the heal csv dd to file
        pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        messageText = "<br><br>" + 'Saved - Success!'
        self.userMessageBox.append(messageText)

    def stata_dta_data_extract_dd(self):
        
        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Stata Dta Data file",
            "FileExplorerOpenFileExt" : "DTA Files (*.dta)",
            "GetDDAction": "Extracted",
            "GetDDActionStatusMessage" : "Extracting metadata to populate HEAL CSV Data Dictionary from Stata Dta data file: ",
            "UtilsInputType" : "stata"
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

        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Redcap CSV Data Dictionary file",
            "FileExplorerOpenFileExt" : "CSV (*.csv *.tsv)",
            "GetDDAction": "Converted",
            "GetDDActionStatusMessage" : "Converting the Redcap CSV Data Dictionary at this path to HEAL CSV Data Dictionary: ",
            "UtilsInputType" : "redcap-csv"
        }

        self.get_heal_csv_dd(get_dd_dict=get_dd_dict)
        
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input Redcap CSV Data Dictionary file", QtCore.QDir.homePath(), "CSV (*.csv *.tsv)")
        
        # ifname = os.path.splitext(str(ifileName))[0].split("/")[-1]

        # messageText = 'Converting the Redcap CSV Data Dictionary at this path to HEAL CSV Data Dictionary: ' + ifileName 
        # self.userMessageBox.setText(messageText)      
       
        # #outputFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Output Directory Where HEAL CSV Data Dictionary Should Be Saved!')
        
        # mydicts = convert_to_vlmd(
        #     input_filepath=ifileName,
        #     data_dictionary_props={
        #         "title":"my dd title",
        #         "description":"my dd description"
        #     },
        #     inputtype="redcap-csv",
        #     output_csv_quoting=True
        # )

        # messageText = messageText + '\n\n\n' + 'Converted - Success!'
        # self.userMessageBox.setText(messageText)

        # ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HEAL CSV Data Dictionary File", 
        #                (QtCore.QDir.homePath() + "/" + "heal-csv-dd-" + ifname + ".csv"),"CSV Files (*.csv)") 

        # messageText = messageText + '\n\n\n' + 'Your HEAL CSV data dictionary will be saved as: ' + ofileName
        # self.userMessageBox.setText(messageText)

        # # write just the heal csv dd to file
        # pd.DataFrame(mydicts['csvtemplate']).to_csv(ofileName, index = False)

        # messageText = messageText + '\n\n\n' + 'Saved - Success!'
        # self.userMessageBox.setText(messageText) 

    def xlsx_data_infer_dd(self,exceltype):
        

        inputmess = "Inferring minimal HEAL CSV Data Dictionary(s) from the XLSX data file at this path ({}):"
        
        if exceltype == "multiple":
            text = "one Data Dictionary per tab"
            multiple_data_dicts = True
            sheet_name = None
        elif exceltype == "combined":
            text = "one Data Dictionary across all tabs"
            multiple_data_dicts = False
            sheet_name = None
        elif exceltype == "first":
            text = "one Data Dictionary for just the first tab"
            multiple_data_dicts = False
            sheet_name = 0
        else:
            raise Exception("Need to specify one of: multiple,combined, or first")

        get_dd_dict = {
            "FileExplorerOpenMessage" : "Select Input Excel (xlsx) File",
            "FileExplorerOpenFileExt" : "XLSX (*.xlsx)",
            "GetDDAction": "Inferred",
            "GetDDActionStatusMessage" : inputmess.format(text),
            "UtilsInputType" : "excel-data"
        }

        #self.get_heal_csv_dd(get_dd_dict=get_dd_dict)

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

        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select your DSC Folder - your Data Dictionary(s) will be saved there:')
        baseDDName = "heal-csv-dd-" + ifname 
        
        print(baseDDName)
        
        
        for name,dictionary in mydicts.items():

            stemsuffix = "" if name == "one" else f"{name}"
            fullDDName = baseDDName + stemsuffix + ".csv" if name == "one" else baseDDName + "-" + stemsuffix + ".csv" 
            
            #ofileName = baseDDName + stemsuffix + ".csv" if name == "one" else baseDDName + "-" + stemsuffix + ".csv" 
            ofileName = os.path.join(folderpath,fullDDName)
            print(ofileName)
            
            
            
            # ofileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, f"Save the {name} worksheet to a HEAL CSV Data Dictionary File", 
            #             (QtCore.QDir.homePath() + "/" + ifname +stemsuffix+ ".csv"),"CSV Files (*.csv)") 

            messageText = messageText + '\n\n\n' + 'Your HEAL CSV Data Dictionary will be saved as: ' + ofileName
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
