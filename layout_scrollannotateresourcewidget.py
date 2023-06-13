import sys
import os
from json import dumps, loads

from qtpy import QtWidgets

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

#from schema_resource_tracker import schema_resource_tracker
from form_schema_resource_tracker import form_schema_resource_tracker
from dsc_pkg_utils import qt_object_properties, get_multi_like_file_descriptions
import pandas as pd

from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QTextCursor
import sys

from pathlib import Path


from layout_fileurladdwidget import ListboxWidget
import re
from copy import deepcopy

class ScrollAnnotateResourceWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Annotate Resource")
        self.initUI()

    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.mfilehbox = QtWidgets.QHBoxLayout()
        
        self.saveFolderPath = None
        self.saveFilePath = None
        ################################## Create component widgets - form, save button, status message box
        # Create the form widget 
        #builder = WidgetBuilder()

        self.schema = form_schema_resource_tracker
        self.ui_schema = {}
        #ui_schema = {
        #    "path": {
        #        "ui:widget": "filepath"
        #    }
        #    ,
        #    "assoc.file.dd": {
        #        "ui:widget": "filepath"
        #    },
        #    "assoc.file.protocol": {
        #        "ui:widget": "filepath"
        #    },
        #    "assoc.file.id.map": {
        #        "ui:widget": "filepath"
        #    },
        #    "assoc.file.id.map": {
        #        "ui:widget": "filepath"
        #    }
        #}

        self.builder = WidgetBuilder(self.schema)
        self.form = self.builder.create_form(self.ui_schema)
        
        #self.form = builder.create_form(schema, ui_schema)
        self.form.widget.state = {
            "resource.id": "resource-1",
            "exp.belongs.to": "exp-999",
            "access.date": "2099-01-01"
            #"schema_path": "some_file.py",
            #"integerRangeSteps": 60,
            #"sky_colour": "#8f5902"
        }

      
        #print(self.form.widget.widgets, type(self.form.widget.widgets))
        #for i in self.form.widget.widgets:
        #    print(i)
        #   #print(type(i))
        
        #self.toolTipContentList = []
        
        #for key, value in self.form.widget.widgets.items():
        #    name = key
        #    print(name)
        #    widget = value
        #    print(widget)
        #    print(type(widget))

        #    toolTipContent = schema["properties"][name]["description"] 
        #    print(toolTipContent)
        #    widget.setToolTip(toolTipContent)
            #self.toolTipContentList.append(toolTipContent)
            #print(self.form.widget.widgets.itemAt(i).widget())
            #widget.setToolTip("" if error is None else error.message)  # TODO
            #widget.setToolTip("hello")  # TODO
        
        # initialize tool tip for each form field based on the description text for the corresponding schema property
        self.add_tooltip()
        self.add_priority_highlight()

        # check for emptyp tooltip content whenever form changes and replace empty tooltip with original tooltip content
        # (only relevant for fields with in situ validation - i.e. string must conform to a pattern - as pyqtschema will replace the 
        # tooltip content with some error content, then replace the content with empty string once the error is cleared - this check will
        # restore the original tooltip content - for efficiency, may want to only run this when a widget that can have validation 
        # errors changes - #TODO)
        self.form.widget.on_changed.connect(self.check_tooltip)
        #self.form.widget.on_changed.connect(self.check_priority_highlight)

        # create 'add dsc data pkg directory' button
        self.buttonAddDir = QtWidgets.QPushButton(text="Add DSC Package Directory",parent=self)
        self.buttonAddDir.clicked.connect(self.add_dir)

        self.buttonAddDir.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )

        # create save button
        self.buttonSaveResource = QtWidgets.QPushButton(text="Save resource",parent=self)
        self.buttonSaveResource.clicked.connect(self.save_resource)

        self.buttonSaveResource.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )

        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)

        # create button to add multiple like resources
        self.buttonAddMultiResource = QtWidgets.QPushButton(text="Add Multiple \'like\' Resources",parent=self)
        self.buttonAddMultiResource.clicked.connect(self.add_multi_resource)
        self.labelAddMultiResource = QtWidgets.QLabel(text="To add multiple 'like' resources, <b>drag and drop file paths right here</b>. If you are annotating a single file, you can drag and drop it here or browse to the file using the File Path field in the form below.",parent=self)
        self.labelApplyNameConvention = QtWidgets.QLabel(text="To apply a naming convention when adding multiple 'like' resources that share a naming convention, <b>add your naming convention in the Name Convention field in the form below</b>, then come back and <b>click the Apply Name Convention button right here</b> to apply. This will autogenerate a minimal description based on the naming convention for each of your 'like' files." + "\n\n" + "e.g." + "\n" + "Name Convention: subject_{subject ID}_day_{date of data collection in YYYYMMDD})" + "\n" + "Example File Name: subject_A1_day_20230607)" + "\n" + "Autogenerated File Description: subject ID: A1, date of data collection in YYYYMMDD: 20230607)",parent=self)

        self.labelAddMultiResource.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.labelApplyNameConvention.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )

        self.labelAddMultiResource.setWordWrap(True)
        self.labelApplyNameConvention.setWordWrap(True)
        
        self.labelAddMultiResource.hide()
        self.labelApplyNameConvention.hide()

        # create button to apply naming convention for multiple like resources
        self.buttonApplyNameConvention = QtWidgets.QPushButton(text="Apply Name Convention",parent=self)
        self.buttonApplyNameConvention.clicked.connect(self.apply_name_convention)
        self.buttonApplyNameConvention.hide()
        
                
        # create drag and drop window for multiple like file addition
        self.lstbox_view = ListboxWidget(self)
        self.lwModel = self.lstbox_view.model()
        self.items = []
        self.lwModel.rowsInserted.connect(self.get_items_list)
        self.lwModel.rowsRemoved.connect(self.get_items_list)
        self.lstbox_view.hide()
        
        ################################## Finished creating component widgets
        #self.mfilehbox.addWidget(self.buttonAddMultiResource)
        #self.mfilehbox.addWidget(self.buttonApplyNameConvention)

        self.vbox.addWidget(self.buttonAddDir)
        self.vbox.addWidget(self.buttonSaveResource)
        self.vbox.addWidget(self.userMessageBox)
        
        self.vbox.addWidget(self.buttonAddMultiResource)
        
        #self.vbox.addLayout(self.mfilehbox)
        self.vbox.addWidget(self.labelAddMultiResource)
        self.vbox.addWidget(self.lstbox_view)
        self.vbox.addWidget(self.labelApplyNameConvention)
        self.vbox.addWidget(self.buttonApplyNameConvention)

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
        #self.show()

        return
        
    def add_priority_highlight(self):

        print(self.form.widget.layout())

        self.formLabelWidgetList = []
        self.formLabelWidgetTextList = []
        self.formLabelWidgetTypeList = []
        
        l = self.form.widget.layout() # get form widget layout (it's a qgridlayout)
        
        wList = (l.itemAt(i).widget() for i in range(l.count())) # get a list of the widgets in the layout
        for idx, w in enumerate(wList): # collect all the qlabel widgets in the layout (for array widgets you have to collect the title instead)
            #print(w.text)
            print("widget: %s  - %s" %(w.objectName(), type(w)))
            
            if isinstance(w, QLabel):
                print("label: %s" %(w.text()))
                self.formLabelWidgetList.append(w)
                self.formLabelWidgetTextList.append(w.text())
                self.formLabelWidgetTypeList.append("label")
            
            if isinstance(w, QGroupBox):
                print("gbtitle: %s" %(w.title()))
                self.formLabelWidgetList.append(w)
                self.formLabelWidgetTextList.append(w.title())
                self.formLabelWidgetTypeList.append("groupbox")
                
        for key, value in self.form.widget.widgets.items():
            fColor = None
            name = key
            widget = value
            
            titleContent = self.schema["properties"][name]["title"] 
            priorityContent = self.schema["properties"][name]["priority"]
            
            if titleContent in self.formLabelWidgetTextList:
                labelWidgetIdx = self.formLabelWidgetTextList.index(titleContent)
                labelWidget = self.formLabelWidgetList[labelWidgetIdx]
                labelWidgetType = self.formLabelWidgetTypeList[labelWidgetIdx]

           
                if "all" in priorityContent:
                    if "high" in priorityContent:
                        fColor = "green"
                
                else:
                    fColor = "gray"

                if fColor: 
                    if (labelWidgetType == "label"):
                        labelWidget.setText('<font color = ' + fColor + '>' + labelWidget.text() + '</font>')
                    if (labelWidgetType == "groupbox"):
                        #labelWidget.setTitle('<font color = ' + fColor + '>' + labelWidget.title() + '</font>')
                        labelWidget.setStyleSheet('QGroupBox  {color: ' + fColor + ';}')


    def add_tooltip(self):
        
        self.toolTipContentList = []
        self.formWidgetNameList =  []
        self.formWidgetList = []

        
        for key, value in self.form.widget.widgets.items():
            name = key
            print(name)
            widget = value
            print(widget)
            print(type(widget))
            #print(widget.items())

            toolTipContent = self.schema["properties"][name]["description"] 
            #if self.schema["properties"][name]["priority"] == "all, high":
            #    p = widget.palette()
            #    p.setColor(widget.backgroundRole(), Qt.red)
            #    widget.setPalette(p)

            print(toolTipContent)
            widget.setToolTip(toolTipContent)
            self.toolTipContentList.append(toolTipContent)
            
            self.formWidgetNameList.append(name)
            self.formWidgetList.append(widget)
            

    def check_tooltip(self):
        i = 0
        for key, value in self.form.widget.widgets.items():
            name = key
            #print(name)
            widget = value
            #print(widget)
            #print(type(widget))

            toolTipContent = widget.toolTip() # get current tool tip content
            #print(toolTipContent)
            if not toolTipContent: # check if the tool tip string is empty (this will occur if a validation error happened and error message was displayed and then the error was resolved as tooltip will be set to empty by pyqtschema pkg upon clearing the error)
                widget.setToolTip(self.toolTipContentList[i]) # if empty then set it to the tooltip content from schema description that was stored on initialization

            i+=1 # increment

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

        self.resIdNum = resIdNum
        self.resource_id = 'resource-'+ str(self.resIdNum)
        self.resourceFileName = 'resource-trk-'+ self.resource_id + '.txt'
        self.saveFilePath = os.path.join(self.saveFolderPath,self.resourceFileName)

        self.messageText = self.messageText + "Based on other resources already saved in your DSC Package directory, your new resource will be saved with the unique ID: " + self.resource_id + "\n" + "Resource ID has been added to the resource form."
        self.messageText = self.messageText + "\n"  + "Your new resource file will be saved in your DSC Package directory as: " + self.saveFilePath + "\n\n"
        self.userMessageBox.setText(self.messageText)
        #self.userMessageBox.moveCursor(QTextCursor.End)

        self.form.widget.state = {
            "resource.id": self.resource_id
        }
        
    def get_items_list(self):
        #item = QListWidgetItem(self.lstbox_view.currentItem())
        #print(item.text())
        lw = self.lstbox_view

        self.items = [lw.item(x).text() for x in range(lw.count())]
        print(self.items)  
        #print(type(self.items)) 

        self.form.widget.state = {
            "path": self.items[0]
        } 

        #if len(self.items) > 1:


    def add_multi_resource(self):

        if ((self.lstbox_view.isHidden()) and (self.labelAddMultiResource.isHidden())):
            self.lstbox_view.show()
            self.labelAddMultiResource.show()
        else:
            self.lstbox_view.hide()
            self.labelAddMultiResource.hide()

    def apply_name_convention(self):
        # have to do this after add_tooltip because these items are defined in that function - may want to change that at some point
        # get the name convention widget 
        # if the contents of the name convention widget
        self.nameConventionWidgetIdx = self.formWidgetNameList.index("description.file.name.convention")
        self.nameConventionWidget = self.formWidgetList[self.nameConventionWidgetIdx] 
        print("my state: ", self.nameConventionWidget.state)
        self.nameConvention = self.nameConventionWidget.state

        try:
            #found = re.search('{(.+?)}', self.nameConvention).group(1)
            nameConventionExplanatoryList = re.findall('{(.+?)}', self.nameConvention)
        except AttributeError:
            # {} not found in the original string
            nameConventionExplanatoryList = '' # apply your error handling
            print('you have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}')
            return

        # get just file stems from full path, this also removes file extensions
        if self.items:
            self.fileStemList = [Path(p).stem for p in self.items]
        else:
            self.fileStemList = [Path(self.form.widget.state["path"]).stem]
        
        self.itemsDescriptionList = get_multi_like_file_descriptions(self.nameConvention, self.fileStemList)

        self.form.widget.state = {
            "description.file": self.itemsDescriptionList[0]
        } 
    
    def save_resource(self):
        
        # check that a dsc data package dir has been added - this is the save folder
        if not self.saveFolderPath:
            messageText = "You must add a DSC Data Package Directory before saving your resource file. Please add a DSC Data Package Directory and then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # check that file path and at least a minimal description has been added to the form 
        # if not exit with informative error
        if not ((self.form.widget.state["path"]) and (self.form.widget.state["description"])):
            messageText = "You must add a resource file path and at least a minimal description of your resource to your resource file form before saving your resource file. Please add a resource file path either by browsing to the file path using the Resource File Path field in the form, or by dragging and dropping the file path for your resource file (or multiple file paths if you are annotating multiple 'like' resources at once) in the drag and drop box above the form, and add at least a minimal description of your resource (or set of 'like' resources) in the Resource Description field in the form. Then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return


        # check if user has modified the resource id from the one that was autogenerated when adding dsc data dir for saving
        # this may happen if for example a user annotates a resource using the autogenerated resource id, then wants to keep 
        # going using the same form window instance, modify the contents to annotate a new resource (perhaps one with some 
        # form fields that will be the same), and save again with a new resource id - in this case the user can modify the 
        # resource id manually, incrementing the id number by one - if resource id modified, updated it in memory and regenerate
        # the save file name, save file path, and resource id number
        if self.form.widget.state["resource.id"] != self.resource_id:
            
            self.resource_id = self.form.widget.state["resource.id"]
            self.resourceFileName = 'resource-trk-'+ self.resource_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.resourceFileName)

            self.resIdNum = int(self.resource_id.split("-")[1])

        # if the user used the drag and drop to add multiple files, get a list of resource ids num, resource id, resource file name, and resource file save path for each file added
        
        self.resIdNumList = [self.resIdNum]
        self.resource_id_list = []
        self.resourceFileNameList = []
        self.saveFilePathList = []
        
        # assign a resource id to every resource file path added, construct a save file path for each resource
        if self.items:
            if len(self.items) > 1:
                
                
                resCounter = 1
                for i in self.items[1:]:
                    
                    self.resIdNumList.append(self.resIdNum + resCounter)
                    print(self.resIdNumList)
                    resCounter += 1

                self.resource_id_list = ["resource-" + str(l) for l in self.resIdNumList]
                print(self.resource_id_list)
                self.resourceFileNameList = ["resource-trk-" + l + ".txt" for l in self.resource_id_list]
                print(self.resourceFileNameList)
                self.saveFilePathList = [os.path.join(self.saveFolderPath,l) for l in self.resourceFileNameList]
                print(self.saveFilePathList)

            else:
                self.resource_id_list = [self.resource_id]
                self.resourceFileNameList = [self.resourceFileName]
                self.saveFilePathList = [self.saveFilePath]
                self.items = [self.form.widget.state["path"]]
                self.itemsDescriptionList = [self.form.widget.state["description.file"]]
        else:
            self.resource_id_list = [self.resource_id]
            self.resourceFileNameList = [self.resourceFileName]
            self.saveFilePathList = [self.saveFilePath]
            self.items = [self.form.widget.state["path"]]
            self.itemsDescriptionList = [self.form.widget.state["description.file"]]
                
                    
        #messageText = ""

        successResIdList = []
        successSaveFilePathList = []
        failResIdList = []
        failSaveFilePathList = []

        for idx, p in enumerate(self.saveFilePathList):
        
            # check if saveFilePath already exists (same as if a file for this resource id already exists); if exists, exit our with informative message;
            # otherwise go ahead and save
            if os.path.isfile(p):
                #messageText = "A resource file for a resource with id " + self.resource_id_list[idx] + " already exists at " + self.saveFilePathList[idx] + "\n\n" + "You may want to do one or both of: 1) Use the View/Edit tab to view your resource tracker file and check which resource IDs you've already used and added to your tracker, 2) Use File Explorer to navigate to your DSC Data Package Directory and check which resource IDs you've already used and for which you've already created resource files - these files will be called \'resource-trk-resource-{a number}.txt\'. While you perform these checks, your resource tracker form will remain open unless you explicitly close it. You can come back to it, change your resource ID, and hit the save button again to save with a resource ID that is not already in use. If you meant to overwrite a resource file you previously created for an resource with this resource ID, please delete the previously created resource file and try saving again." + "\n\n" 
                #errorFormat = '<span style="color:red;">{}</span>'
                #self.userMessageBox.append(errorFormat.format(messageText))
                failSaveFilePathList.append(p)
                failResIdList.append(self.resource_id_list[idx])
            else:
                successSaveFilePathList.append(p)
                successResIdList.append(self.resource_id_list[idx])

                
            if failResIdList:
                print("something went wrong - check the resource id in your form - do you already have a resource file saved for a resource with this resource id? if not, did you add multiple like resource files? resource ids will be autogenerated for all of the resource files you added - IDs will be generated by adding 1 to the resource id in your form for each file in turn - do you already have a resource file saved for a resource with one of the resource ids that may have been autogenerated based on this approach? the safest thing to do is to check the resource files you have saved in your dsc package folder, find the highest resource id number for which you have created/saved a resource file, and enter your resource id in the form as having an id number one higher than the max resource id number you identified - then try saving again - if you add your dsc package directory using the push button at the top of the form window, a resource id will be autogenerated for you using this approach automatically.")
                return
            else:
                print(self.form.widget.state)
                resource = self.form.widget.state

                
                for idx, p in enumerate(self.saveFilePathList):
                    
                    currentResource = deepcopy(resource)
                    
                    currentResource["resource.id"] = self.resource_id_list[idx]
                    currentResource["path"] = self.items[idx]
                    currentResource["description.file"] = self.itemsDescriptionList[idx]

                    f=open(p,'w')
                    print(dumps(currentResource, indent=4), file=f)
                    f.close()
                
                if len(self.saveFilePathList) > 1:
                    myString1 = "files were"
                    myString2 = ', '.join(self.saveFilePathList)
                else: 
                    myString1 = "file was"
                    myString2 = self.saveFilePathList[0]

                #self.messageText = self.messageText + '\n\n' + "Your resource file was successfully written at: " + self.saveFilePath + '\n' + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
                messageText = "Your resource " + myString1 + " successfully written at: " + myString2 + "\n\n" + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file." + "\n\n"
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