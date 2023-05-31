import sys
import os
from json import dumps, loads

from qtpy import QtWidgets

from qt_jsonschema_form import WidgetBuilder

#from schema_resource_tracker import schema_resource_tracker
from form_schema_resource_tracker import form_schema_resource_tracker
from dsc_pkg_utils import qt_object_properties
import pandas as pd

from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QTextCursor
import sys

from pathlib import Path

class ScrollAnnotateResourceWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Annotate Resource")
        self.initUI()

    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        ################################## Create component widgets - form, save button, status message box
        # Create the form widget 
        builder = WidgetBuilder()

        schema = form_schema_resource_tracker
        ui_schema = {
            "path": {
                "ui:widget": "filepath"
            }
            ,
            "assoc.file.dd": {
                "ui:widget": "filepath"
            },
            "assoc.file.protocol": {
                "ui:widget": "filepath"
            },
            "assoc.file.id.map": {
                "ui:widget": "filepath"
            },
            "assoc.file.id.map": {
                "ui:widget": "filepath"
            }
        }

        self.form = builder.create_form(schema, ui_schema)
        self.form.widget.state = {
            "resource.id": "resource-1",
            "exp.belongs.to": "exp-999",
            "access.date": "2099-01-01"
            #"schema_path": "some_file.py",
            #"integerRangeSteps": 60,
            #"sky_colour": "#8f5902"
        }
        
        # create 'add dsc data pkg directory' button
        self.buttonAddDir = QtWidgets.QPushButton(text="Add DSC Package Directory",parent=self)
        self.buttonAddDir.clicked.connect(self.add_dir)

        # create save button
        self.buttonSaveResource = QtWidgets.QPushButton(text="Save resource",parent=self)
        self.buttonSaveResource.clicked.connect(self.save_resource)

        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)
        
        ################################## Finished creating component widgets

        self.vbox.addWidget(self.buttonAddDir)
        self.vbox.addWidget(self.buttonSaveResource)
        self.vbox.addWidget(self.userMessageBox)
        self.vbox.addWidget(self.form)
        

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle("Annotate Resource")
        self.show()

        return
        
        
    def add_dir(self):
        
        self.saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new resource will be saved there!')
        
        # get new resource ID for new resource file - get the max id num used for existing resource files and add 1; if no resource files yet, set id num to 1
        
        resFileList = [filename for filename in os.listdir(self.saveFolderPath) if filename.startswith("resource-trk-resource-")]
        print(resFileList)

        if resFileList: # if the list is not empty
            resFileStemList = [Path(filename).stem for filename in resFileList]
            print(resFileStemList)
            resIdNumList = [int(filename.rsplit('-',1)[1]) for filename in resFileStemList]
            print(resIdNumList)
            resIdNum = max(resIdNumList) + 1
            print(max(resIdNumList),resIdNum)
        else:
            resIdNum = 1

        
        self.resource_id = 'resource-'+ str(resIdNum)
        #resourceFileName = 'resource-trk-resource-'+ str(resIdNum) + '.txt'
        resourceFileName = 'resource-trk-'+ self.resource_id + '.txt'
        self.saveFilePath = os.path.join(self.saveFolderPath,resourceFileName)

        self.messageText = self.messageText + "Based on other resources already saved in your DSC Package directory, your new resource will be saved with the unique ID: " + self.resource_id + "\n" + "Resource ID has been added to the resource form."
        self.messageText = self.messageText + "\n"  + "Your new resource file will be saved in your DSC Package directory as: " + self.saveFilePath + "\n\n"
        self.userMessageBox.setText(self.messageText)
        #self.userMessageBox.moveCursor(QTextCursor.End)

        self.form.widget.state = {
            "resource.id": self.resource_id
        }
        
        

    
    def save_resource(self):
        print(self.form.widget.state)
        resource = self.form.widget.state
        
        
        #saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new resource will be saved there!')
        
        ## get new resource ID for new resource file - get the max id num used for existing resource files and add 1; if no resource files yet, set id num to 1
        
        #resFileList = [filename for filename in os.listdir(saveFolderPath) if filename.startswith("resource-trk-resource-")]
        #print(resFileList)

        #if resFileList: # if the list is not empty
        #    resFileStemList = [Path(filename).stem for filename in resFileList]
        #    print(resFileStemList)
        #    resIdNumList = [int(filename.rsplit('-',1)[1]) for filename in resFileStemList]
        #    print(resIdNumList)
        #    resIdNum = max(resIdNumList) + 1
        #    print(max(resIdNumList),resIdNum)
        #else:
        #    resIdNum = 1

        
        #resource_id = 'resource-'+ str(resIdNum)
        
        #resourceFileName = 'resource-trk-'+ resource_id + '.txt'
        #saveFilePath = os.path.join(saveFolderPath,resourceFileName)
        
        messageText = ""
        
        if os.path.isfile(self.saveFilePath):
            #self.messageText = self.messageText + '\n\n' + "A resource file for a resource with id " + self.resource_id + " already exists at " + self.saveFilePath + '\n' + "You may want to do one or both of: 1) Use the View/Edit tab to view your resource tracker file and check which resource IDs you've already used and added to your tracker, 2) Use File Explorer to navigate to your DSC Data Package Directory and check which resource IDs you've already used and for which you've already created resource files - these files will be called \'resource-trk-resource-{a number}.txt\'. While you perform these checks, your resource tracker form will remain open unless you explicitly close it. You can come back to it, change your resource ID, and hit the save button again to save with a resource ID that is not already in use. If you meant to overwrite a resource file you previously created for an resource with this resource ID, please delete the previously created resource file and try saving again." 
            messageText = "A resource file for a resource with id " + self.resource_id + " already exists at " + self.saveFilePath + "\n\n" + "You may want to do one or both of: 1) Use the View/Edit tab to view your resource tracker file and check which resource IDs you've already used and added to your tracker, 2) Use File Explorer to navigate to your DSC Data Package Directory and check which resource IDs you've already used and for which you've already created resource files - these files will be called \'resource-trk-resource-{a number}.txt\'. While you perform these checks, your resource tracker form will remain open unless you explicitly close it. You can come back to it, change your resource ID, and hit the save button again to save with a resource ID that is not already in use. If you meant to overwrite a resource file you previously created for an resource with this resource ID, please delete the previously created resource file and try saving again." + "\n\n" 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
        else:
            f=open(self.saveFilePath,'w')
            print(dumps(resource, indent=4), file=f)
            f.close()
            #self.messageText = self.messageText + '\n\n' + "Your resource file was successfully written at: " + self.saveFilePath + '\n' + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
            messageText = "Your resource file was successfully written at: " + self.saveFilePath + "\n\n" + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file." + "\n\n"
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

        #saveFormat = '<span style="color:green;">{}</span>'
        #self.userMessageBox.append(saveFormat.format(messageText))
        #self.userMessageBox.setText(self.messageText)
        self.userMessageBox.moveCursor(QTextCursor.End)
        
        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateResourceWindow()
    window.show()
    sys.exit(app.exec_())