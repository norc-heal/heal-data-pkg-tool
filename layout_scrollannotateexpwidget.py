import sys
import os
from json import dumps, loads, load

from qtpy import QtWidgets

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

#from schema_results_tracker import schema_results_tracker
from schema_experiment_tracker import schema_experiment_tracker
from dsc_pkg_utils import qt_object_properties, get_multi_like_file_descriptions
import dsc_pkg_utils
import pandas as pd
import json
import dsc_pkg_utils

from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtGui import QTextCursor
import sys

from pathlib import Path

from healdata_utils.validators.jsonschema import validate_against_jsonschema
import datetime
import jsonschema
from jsonschema import validate


from layout_fileurladdwidget import ListboxWidget
import re
from copy import deepcopy

class ScrollAnnotateExpWindow(QtWidgets.QMainWindow):
    def __init__(self, workingDataPkgDirDisplay, workingDataPkgDir, mode = "add"):
        super().__init__()
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.workingDataPkgDir = workingDataPkgDir
        self.mode = mode
        self.schemaVersion = schema_experiment_tracker["version"]
        self.initUI()

    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.mfilehbox = QtWidgets.QHBoxLayout()
        
        self.saveFolderPath = None
        self.saveFilePath = None
        self.priorityContentList = None

        ################################## Create component widgets - form, save button, status message box
        
        # create the form widget 
        self.schema = schema_experiment_tracker
        self.ui_schema = {}
        
        self.builder = WidgetBuilder(self.schema)
        self.form = self.builder.create_form(self.ui_schema)
        
        self.formDefaultState = {
            "schemaVersion": self.schemaVersion,
            "experimentId": "exp-1",
            "experimentName": "default-experiment-name"
        }

        self.form.widget.state = deepcopy(self.formDefaultState)
      
        #  # create 'add dsc data pkg directory' button
        # self.buttonAddDir = QtWidgets.QPushButton(text="Add DSC Package Directory",parent=self)
        # self.buttonAddDir.clicked.connect(self.add_dir)

        # self.buttonAddDir.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.buttonAddDir.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
                

        # create save button
        self.buttonSaveExperiment = QtWidgets.QPushButton(text="Save experiment",parent=self)
        self.buttonSaveExperiment.clicked.connect(self.save_experiment)

        self.buttonSaveExperiment.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonSaveExperiment.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
        

         # create clear form button
        self.buttonClearForm = QtWidgets.QPushButton(text="Clear form",parent=self)
        self.buttonClearForm.clicked.connect(self.clear_form)

        self.buttonClearForm.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonClearForm.setStyleSheet("QPushButton{background-color:rgba(196,77,86,100);} QPushButton:hover{background-color:rgba(196,30,58,50);}");
        
        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)

        self.labelUserMessageBox = QtWidgets.QLabel(text = "User Status Message Box:", parent=self)
   
        # # create button to add multiple file dependencies addition
        # self.buttonAddMultiDepend = QtWidgets.QPushButton(text="Add Multiple Result Dependencies",parent=self)
        # self.buttonAddMultiDepend.clicked.connect(self.add_multi_depend)
        # self.labelAddMultiDepend = QtWidgets.QLabel(text="To add multiple file dependencies for your result, <b>drag and drop file paths right here</b>. If your result has one or just a few dependencies, you can drag and drop them here or browse to each dependency (one dependency at a time) using the Associated Files/Dependencies field in the form below.",parent=self)
        
        # self.labelAddMultiDepend.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )

        # self.labelAddMultiDepend.setWordWrap(True)

        # # create drag and drop window for multiple file dependencies addition
        # self.lstbox_view2 = ListboxWidget(self)
        # self.lwModel2 = self.lstbox_view2.model()
        # self.items2 = []
        # self.programmaticListUpdate2 = False
        # self.lwModel2.rowsInserted.connect(self.get_items_list2)
        # self.lwModel2.rowsRemoved.connect(self.get_items_list2)
       
        ################################## Apply some initializing and maintenance functions

        # initialize tool tip for each form field based on the description text for the corresponding schema property
        self.add_tooltip()
        self.add_priority_highlight_and_hide()
        self.add_dir()
        if self.mode == "add":
            self.get_id()
        #self.add_priority_highlight()
        #self.initial_hide()

        # check for emptyp tooltip content whenever form changes and replace empty tooltip with original tooltip content
        # (only relevant for fields with in situ validation - i.e. string must conform to a pattern - as pyqtschema will replace the 
        # tooltip content with some error content, then replace the content with empty string once the error is cleared - this check will
        # restore the original tooltip content - for efficiency, may want to only run this when a widget that can have validation 
        # errors changes - #TODO)
        self.form.widget.on_changed.connect(self.check_tooltip)
        #self.formWidgetList[self.formWidgetNameList.index("category")].on_changed.connect(self.conditional_fields)
        self.formWidgetList[self.formWidgetNameList.index("experimentName")].on_changed.connect(lambda saveStatus: self.check_exp_name_unique("check"))
        
        ################################## Finished creating component widgets
        

        #self.vbox.addWidget(self.buttonAddDir)
        self.vbox.addWidget(self.buttonSaveExperiment)
        self.vbox.addWidget(self.buttonClearForm)
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
        
        # self.vbox.addWidget(self.buttonAddMultiDepend)
        # self.vbox.addWidget(self.labelAddMultiDepend)
        # self.vbox.addWidget(self.lstbox_view2)

        self.vbox.addWidget(self.form)
        

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle("Annotate Experiment")
        #self.show()

        return
        
    def scrollScrollArea (self, topOrBottom, minVal=None, maxVal=None):
        # Additional params 'minVal' and 'maxVal' are declared because
        # rangeChanged signal sends them, but we set it to optional
        # because we may need to call it separately (if you need).

        if topOrBottom == "bottom":
    
            self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum()
            )

        if topOrBottom == "top":
    
            self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().minimum()
            )

    # def mousePressEvent(self,event):
    #     print('mouse pressed outside view')
    #     event.accept()

    # def eventFilter(self,object,event):
    #     if object == self.formWidgetList[self.formWidgetNameList.index("experimentName")] and event.type() == QtCore.QEvent.Mouse:
    #         print('mouse pressed inside view')
    #         return True
    #     return super().eventFilter(object,event)

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
    
    def add_priority_highlight_and_hide(self):

        #self.labelAddMultiDepend.hide()
        #self.lstbox_view2.hide()

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

        newList = None

        if not self.priorityContentList:
            newList = True
            self.priorityContentList = []  

        for key, value in self.form.widget.widgets.items():
            fColor = None
            name = key
            widget = value
            
            titleContent = self.schema["properties"][name]["title"] 
            priorityContent = self.schema["properties"][name]["priority"]
            
            if newList:
                self.priorityContentList.append(priorityContent)
            
            if titleContent in self.formLabelWidgetTextList:
                labelWidgetIdx = self.formLabelWidgetTextList.index(titleContent)
                labelWidget = self.formLabelWidgetList[labelWidgetIdx]
                labelWidgetType = self.formLabelWidgetTypeList[labelWidgetIdx]

           
                if ", high" in priorityContent:
                    fColor = "green"
                    if ", auto" in priorityContent:
                        fColor = "blue"
                
                if fColor: 
                    if (labelWidgetType == "label"):
                        labelWidget.setText('<font color = ' + fColor + '>' + labelWidget.text() + '</font>')
                    if (labelWidgetType == "groupbox"):
                        #labelWidget.setTitle('<font color = ' + fColor + '>' + labelWidget.title() + '</font>')
                        labelWidget.setStyleSheet('QGroupBox  {color: ' + fColor + ';}')

                if not priorityContent.startswith("all, "):
                    labelWidget.hide()
                    widget.hide()

   
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

    def check_exp_name_unique(self, saveStatus):
        
        if saveStatus == "save":
            self.uniqueExpNameOnSave = True
        
        self.experimentNameList = []
        self.experimentNameList, self.experimentNameDf = dsc_pkg_utils.get_exp_names(self=self, perResource=True) # gets self.experimentNameList

        print("self.experimentNameList: ",self.experimentNameList)
        currentExperimentName = self.formWidgetList[self.formWidgetNameList.index("experimentName")].text()
        currentExperimentId = self.formWidgetList[self.formWidgetNameList.index("experimentId")].text()
        print("currentExperimentName: ",currentExperimentName)

        if currentExperimentName == "default-experiment-name":
            if saveStatus != "save":
                messageText = "<br>You've re-set the experiment name to the default value of \"default-experiment-name\". This is the equivalent of NOT naming your experiment. If you wish to name your experiment, please enter a unique experiment name that is NOT equal to \"default-experiment-name\". Experiment names already in use include: <br><br>" + "<br>".join(self.experimentNameList)
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
            
            if saveStatus == "save":
                messageText = "<br>Your experiment will be saved with the default experiment name of \"default-experiment-name\". This is the equivalent of NOT assigning an experiment name to your experiment. If you wish to assign an experiment name to your experiment, you can edit your experiment by navigating to the \"Experiment Tracker\" tab >> \"Add Experiment\" sub-tab, clicking on the \"Edit existing experiment\" push-button, opening the form for this experiment, and editing the Experiment Name form field."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))

        elif currentExperimentName in self.experimentNameList:
            # if this experiment name has been used before, check to see if it's been used for another entry in the exp tracker that is for this exp id
            # this may happen if for example user is editing an existing experiment
            # if this is the case, do not throw an error

            currentExperimentNameDf = self.experimentNameDf[self.experimentNameDf["experimentName"] == currentExperimentName]
            currentAssociatedExperimentId = currentExperimentNameDf["experimentId"].tolist()[0]
            print(currentAssociatedExperimentId)

            if currentExperimentId != currentAssociatedExperimentId:

                if saveStatus != "save":
                    messageText = "<br>You've used this experiment name before, and experiment name must be unique - Please enter a unique experiment name. Experiment names already in use include: <br><br>" + "<br>".join(self.experimentNameList)
                    errorFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(errorFormat.format(messageText))

                if saveStatus == "save":
                    messageText = "<br>Your experiment cannot be saved because the experiment name you entered in the Experiment Name form field is not unique. If you want to assign an experiment name to your experiment you must choose a unique experiment name and enter it into the Experiment Name form field, then try saving again. If you do not want to assign an experiment name to your experiment, re-set the value of the Experiment Name form field to \"default-experiment-name\" and try saving again. Experiment names already in use include: <br><br>" + "<br>".join(self.experimentNameList)
                    errorFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(errorFormat.format(messageText))
                    self.uniqueExpNameOnSave = False

        else: 
            if saveStatus != "save": 
                messageText = "<br>Your experiment name is unique! <br><br>" 
                errorFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText)) 

    def toggle_widgets(self, keyText, desiredToggleState):

        indices = [i for i, x in enumerate(self.priorityContentList) if keyText in x.split(", ")]
        print(indices)
        for i in indices:
            labelW = self.formLabelWidgetList[i]
            print(labelW)
            labelWType = self.formLabelWidgetTypeList[i]
            print(labelWType)
            labelWText = self.formLabelWidgetTextList[i]
            print(labelWText)
            fieldW = self.formWidgetList[i]
            print(fieldW)
            fieldWName = self.formWidgetNameList[i]
            print(fieldWName)

            if desiredToggleState == "show":
                labelW.show()
                fieldW.show()
            
            if desiredToggleState == "hide":
                labelW.hide()
                fieldW.hide()
    
    # def conditional_fields(self, changedFieldName):

    #     # this is an inefficient way to make sure previously unhidden fields get hidden again if user changes the category
    #     # should really save the last chosen state and be selective about re-hiding the ones that were revealed due to the
    #     # previous selection

    #     ################### hide fields that were revealed due to previous selection

    #     if self.form.widget.state["category"] != "figure":
    #         self.toggle_widgets(keyText = "figure", desiredToggleState = "hide")
    #         # delete contents of conditional fields if any added
    #         self.form.widget.state = {
    #             "figureNumber": []
    #         }

    #     if self.form.widget.state["category"] != "table":
    #         self.toggle_widgets(keyText = "table", desiredToggleState = "hide")
    #         # delete contents of conditional fields if any added
    #         self.form.widget.state = {
    #             "tableNumber": []
    #         }  
            
    #     ################### show field appropriate to current selection
            
    #     if self.form.widget.state["category"] == "figure":
    #         self.toggle_widgets(keyText = "figure", desiredToggleState = "show")

    #     if self.form.widget.state["category"] == "table":
    #         self.toggle_widgets(keyText = "table", desiredToggleState = "show")
          
    def add_dir(self):
        
        #self.saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new result will be saved there!')
        self.saveFolderPath = self.workingDataPkgDir

    def get_id(self):

        if self.saveFolderPath:

            # get new ID for new annotation file - get the max id num used for existing annotation files and add 1; if no annotation files yet, set id num to 1
        
            annotationFileList = [filename for filename in os.listdir(self.saveFolderPath) if filename.startswith("exp-trk-exp-")]
            print(annotationFileList)

            if annotationFileList: # if the list is not empty
                annotationFileStemList = [Path(filename).stem for filename in annotationFileList]
                print(annotationFileStemList)
                annotationIdNumList = [int(filename.rsplit('-',1)[1]) for filename in annotationFileStemList]
                print(annotationIdNumList)
                annotationIdNum = max(annotationIdNumList) + 1
                print(max(annotationIdNumList),annotationIdNum)
            else:
                annotationIdNum = 1

            self.annotationIdNum = annotationIdNum
            self.annotation_id = 'exp-'+ str(self.annotationIdNum)
            self.annotationFileName = 'exp-trk-'+ self.annotation_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.annotationFileName)

            messageText = "<br>Based on other experiments already saved in your working DSC Data Package directory, your new experiment will be saved with the unique ID: " + self.annotation_id + "<br>Experiment ID has been added to the experiment form."
            messageText = messageText + "<br><br>Your new experiment annotation file will be saved in your working DSC Data Package directory as: " + self.saveFilePath + "<br><br>"
            self.userMessageBox.append(messageText)
            #self.userMessageBox.moveCursor(QTextCursor.End)

            
            self.form.widget.state = {
                "experimentId": self.annotation_id
            }

        # this should no longer be necessary as the form widget will only be opened if a workingDataPkgDir has been set and the path has been as a string 
        else:
            messageText = "<br>Please select your DSC Data Package Directory to proceed."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        
    # def get_items_list2(self):
    #     #item = QListWidgetItem(self.lstbox_view.currentItem())
    #     #print(item.text())
    #     if self.programmaticListUpdate2:
    #         self.programmaticListUpdate2 = False
    #         return

    #     lw = self.lstbox_view2
        
    #     oldLength = None
    #     if self.items2:
    #         oldLength = len(self.items2)
    #         oldItems = self.items2

    #     self.items2 = [lw.item(x).text() for x in range(lw.count())]
    #     print(self.items2)

    #     refactorItems = []
    #     for i in self.items2:
    #         print(i)
    #         if os.path.isdir(i):
    #             #self.programmaticListUpdate = True
    #             myFiles = [os.path.join(i,f) for f in os.listdir(i) if os.path.isfile(os.path.join(i,f))]
    #             print(myFiles)
    #             refactorItems.extend(myFiles)
    #         else:
    #             refactorItems.append(i)

    #     if self.items2 != refactorItems:
    #         self.programmaticListUpdate2 = True

    #         self.items2 = refactorItems
    #         self.lstbox_view2.clear()
    #         self.lstbox_view2.addItems(self.items2)

    #     newLength = len(self.items2)
    #     print(self.items2)  
    #     #print(type(self.items)) 
    #     print(len(self.items2))

    #     if self.items2:
    #         #updatePath = self.items2[0]
    #         updateAssocFileMultiDepend = self.items2
    #     else:
    #         #updatePath = ""
    #         updateAssocFileMultiDepend = []

    #     self.form.widget.state = {
    #         #"path": updatePath,
    #         "associatedFileDependsOn": updateAssocFileMultiDepend
    #     } 

        
    
    #     if oldLength:
    #         if ((oldLength > 0) and (newLength == 0)):
    #             print("hide")
                
    #             self.labelAddMultiDepend.hide()
    #             self.lstbox_view2.hide()
                
    # def add_multi_depend(self):

    #     if ((self.lstbox_view2.isHidden()) and (self.labelAddMultiDepend.isHidden())):
    #         self.lstbox_view2.show()
    #         self.labelAddMultiDepend.show()
    #     else:
    #         self.lstbox_view2.hide()
    #         self.labelAddMultiDepend.hide()

    def save_experiment(self):
        
        # this should no longer be necessary as the form will only be opened if a valid working data pkg dir has been set by the user and the path has been passed as a string to the form widget
        # check that a dsc data package dir has been added - this is the save folder
        if not self.saveFolderPath:
            messageText = "<br>You must add a DSC Data Package Directory before saving your experiment annotation file. Please add a DSC Data Package Directory and then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # check that at least a minimal description has been added to the form 
        # if not exit with informative error
        if not (self.form.widget.state["experimentDescription"]):
            messageText = "<br>You must add at least a minimal description of your experiment before saving your experiment annotation file. Please add at least a minimal description of your experiment in the Experiment Description field in the form. Then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        #self.buttonXlsxDataInferCombinedHealCsvDd.clicked.connect(lambda exceltype: self.xlsx_data_infer_dd("combined"))
        self.check_exp_name_unique("save") # this checks if experimentName is unique, if not sets self.uniqueExpNameOnSave to False, also outputs informative message if exp name is not unique or if it is left/set at the default value of default-experiment-name
        if not self.uniqueExpNameOnSave:
            return
             
        
        # check if user has modified the exp id from the one that was autogenerated when adding dsc data dir for saving
        # this may happen if for example a user annotates an experiment using the autogenerated id, then wants to keep 
        # going using the same form window instance, modify the contents to annotate a new experiment (perhaps one with some 
        # form fields that will be the same), and save again with a new id - in this case the user can modify the 
        # id manually, incrementing the id number by one - if id modified, updated it in memory and regenerate
        # the save file name, save file path, and id number
        if self.form.widget.state["experimentId"] != self.annotation_id:
            
            self.annotation_id = self.form.widget.state["experimentId"]
            self.annotationFileName = 'exp-trk-'+ self.annotation_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.annotationFileName)

            self.annotationIdNum = int(self.annotation_id.split("-")[1])
        
        # check if saveFilePath already exists (same as if a file for this experiment id already exists); if exists, exit our with informative message;
        # otherwise go ahead and save
        if os.path.isfile(self.saveFilePath):
            messageText = "An experiment annotation file for an experiment with id " + self.annotation_id + " already exists at " + self.saveFilePath + "<br><br>You may want to do one or both of: 1) Use the View/Edit tab to view your experiment tracker file(s) and check which experiment IDs you've already used and added to your tracker, 2) Use File Explorer to navigate to your DSC Data Package Directory and check which experiment IDs you've already used (i.e. for which you've already created experiment annotation files - these files will be called \'exp-trk-exp-{a number}.txt\'. While you perform these checks, your experiment tracker form will remain open unless you explicitly close it. You can come back to it, change your experiment ID, and hit the save button again to save with an experiment ID that is not already in use. If you meant to overwrite an experiment annotation file you previously created for an experiment with this experiment ID, please delete the previously created experiment annotation file and try saving again.<br><br>" 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        else:
                              
            annotationContent = self.form.widget.state
            f=open(self.saveFilePath,'w')
            print(dumps(annotationContent, indent=4), file=f)
            f.close()
                
            #self.messageText = self.messageText + '\n\n' + "Your resource file was successfully written at: " + self.saveFilePath + '\n' + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
            #messageText = "<br>Your experiment was successfully written at: " + self.saveFilePath + "<br><br>You'll want to head back to the \'Add Experiment\' tab and use the \'Add Experiment\' button to add this experiment file to your experiment tracker file! You can do this now, or later - You can add experiment files to an experiment tracker file one at a time, or you can add multiple experiment files all at once, so you may choose to create experiment files for several/all of your experiments and then add them in one go to your experiment tracker file."
            messageText = "<br>Your experiment was successfully written at: " + self.saveFilePath + "<br><br> Starting to add your experiment to the Experiment Tracker now! See below for updates: <br>"
            
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            self.userMessageBox.moveCursor(QTextCursor.End)

            QApplication.processEvents() # print accumulated user status messages 

            self.add_exp() # add experiment file to experiment tracker

    def add_exp(self):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br> The experiment was saved but was not added to the Experiment Tracker. To add this experiment to your Experiment Tracker, first set your working Data Package Directory, then navigate to the \"Experiment Tracker\" tab >> \"Add Experiment\" sub-tab and click on the \"Batch add experiment(s) to tracker\" push-button. You can select just this experiment, or all experiments to add to the Experiment Tracker. If some experiments you select to add to the Experiment Tracker have already been added they will be not be re-added."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
                messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br><br>The experiment was saved but was not added to the Experiment Tracker. To add this experiment to your Experiment Tracker, first set your working Data Package Directory, then navigate to the \"Experiment Tracker\" tab >> \"Add Experiment\" sub-tab and click on the \"Batch add experiment(s) to tracker\" push-button. You can select just this experiment, or all experiments to add to the Experiment Tracker. If some experiments you select to add to the Experiment Tracker have already been added they will be not be re-added."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

        # get result file path
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Result Txt Data file(s)",
        #        (QtCore.QDir.homePath()), "Text (*.txt)")

        # open files select file browse to working data package directory
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Experiment Txt Data file(s) from your working Data Package Directory",
        #        self.workingDataPkgDir, "Text (*.txt)")

        ifileName = [self.saveFilePath]
        
        if ifileName:
            
            # this check shouldn't be required here anymore  
            # just for the first annotation file selected for addition to the tracker, check to make sure it is 
            # in the working data pkg dir - if not return with informative message
            ifileNameCheckDir = ifileName[0]

            # if user selects a result txt file that is not in the working data pkg dir, return w informative message
            if Path(self.workingDataPkgDir) != Path(ifileNameCheckDir).parent:
                messageText = "<br>You selected an experiment txt file that is not in your working Data Package Directory; You must select an experiment txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #countFiles = len(ifileName)

            # initialize lists to collect valid and invalid files
            validFiles = []
            invalidFiles = []
            
            # initialize an empty dataframe to collect data from each file in ifileName
            # one row will be added to collect_df for each valid file in ifileName
            collect_df = pd.DataFrame([])
            
            for filename in ifileName:
                print(filename)

                # get exp id and filename stem
                ifileNameStem = Path(filename).stem
                IdNumStr = ifileNameStem.rsplit('-',1)[1]
                annotation_id = "exp-" + IdNumStr
                print("exp-id: ", annotation_id)
                
                # load data from annotation file and convert to python object
                #path = ifileName
                path = filename
                data = json.loads(Path(path).read_text())
                print(data)

                # validate annotation file json content against tracker json schema
                out = validate_against_jsonschema(data, schema_experiment_tracker)
                print(out["valid"])
                print(out["errors"])
                print(type(out["errors"]))

                
                # if not valid, print validation errors and exit 
                if not out["valid"]:

                    # add file to list of invalid files
                    invalidFiles.append(ifileNameStem)
                    
                    # get validation errors to print
                    printErrListSingle = []
                    # initialize the final full validation error message for this file to start with the filename
                    printErrListAll = [ifileNameStem]
                
                    for e in out["errors"]:
                        printErrListSingle.append(''.join(e["absolute_path"]))
                        printErrListSingle.append(e["validator"])
                        printErrListSingle.append(e["validator_value"])
                        printErrListSingle.append(e["message"])

                        print(printErrListSingle)
                        printErrSingle = '\n'.join(printErrListSingle)
                        printErrListAll.append(printErrSingle)

                        printErrListSingle = []
                        printErrSingle = ""
                    
                    printErrAll = '\n\n'.join(printErrListAll)
                
                    #messageText = "The following resource file is NOT valid and will not be added to your Resource Tracker file: " + ifileName + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + ', '.join(out["errors"]) + "\n\n\n" + "Exiting \"Add Resource\" function now."
                    messageText = "The following experiment file is NOT valid and will not be added to the Experiment Tracker file: " + filename + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + printErrAll + "\n\n\n"
                    
                    self.userMessageBox.append(messageText)
                    #return
                    # switch from return to break so that if user selects more than one file, and one is not valid, can skip to next file and continue instead of returning fully out of the function
                    #break
                    continue 

                # if valid, continue:
                else:
                    #messageText = "The following resource file is valid: " + ifileName
                    messageText = "The following experiment file is valid: " + filename
                    self.userMessageBox.append(messageText)

                    # add file to list of valid files
                    validFiles.append(ifileNameStem)
                    print("valid files:", validFiles)

                    # get result annotation file creation and last modification datetime
                    restrk_c_timestamp = os.path.getctime(filename)
                    restrk_c_datetime = datetime.datetime.fromtimestamp(restrk_c_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("restrk_c_datetime: ", restrk_c_datetime)
        
                    restrk_m_timestamp = os.path.getmtime(filename)
                    restrk_m_datetime = datetime.datetime.fromtimestamp(restrk_m_timestamp).strftime("%Y-%m-%d, %H:%M:%S")
                    print("restrk_m_datetime: ", restrk_m_datetime)

                    # add_to_df_dict = {#"resultId":[resource_id],
                    #                 "experimentIdNumber": [int(IdNumStr)],  
                    #                 #"annotationCreateDateTime": [restrk_c_datetime],
                    #                 #"annotationModDateTime": [restrk_m_datetime],
                    #                 "annotationModTimeStamp": [restrk_m_timestamp]}


                    # add_to_df = pd.DataFrame(add_to_df_dict)

                    # convert json to pd df
                    df = pd.json_normalize(data) # df is a one row dataframe
                    print(df)
                    df["annotationCreateDateTime"][0] = restrk_c_datetime
                    df["annotationModDateTime"][0] = restrk_m_datetime
                    df["experimentIdNumber"][0] = int(IdNumStr)
                    df["annotationModTimeStamp"] = restrk_m_timestamp
                    print(df)
                    # df = pd.concat([df,add_to_df], axis = 1) # concatenate cols to df; still a one row dataframe
                    # print(df)

                    collect_df = pd.concat([collect_df,df], axis=0) # add this files data to the dataframe that will collect data across all valid data files
                    print("collect_df rows: ", collect_df.shape[0])

                    
        else: 
            print("you have not selected any files; returning")
            messageText = "<br>You have not selected any experiment files to add to the experiment tracker. Please select at least one experiment file to add."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # once you've looped through all selected files, if none are valid, print an informative message for the user listing
        # which files did not pass validation and exit
        if not validFiles:
            messageText = "The contents of the Experiment file(s): " + "\n\n\n" + ', '.join(invalidFiles) + "\n\n\n" + "cannot be added to an Experiment Tracker file because they did not pass validation. Please review the validation errors for the file(s) printed above." + "Exiting \"Add Experiment\" function now." 
            self.userMessageBox.append(messageText)
            return

        
        
        # you should now have collected one row of data from each valid data file and collected it into collect_df dataframe
        # now get location of dsc pkg dir, check if appropriate results trackers already exist, if not create them, then add
        # results to appropriate results trackers

        # no longer need to ask user to browse to dsc data package dir - instead use working data package dir set by user in data package tab of tool
        #dscDirPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your result(s) will be auto-added to appropriate Results Tracker(s) there!')
        dscDirPath = self.workingDataPkgDir
        

        # this check should no longer be necessary
        if not dscDirPath:
            messageText = "You have not selected a directory. Please select your DSC Data Package Directory. If you have not yet created a DSC Data Package Directory, use the \"Create New Data Package\" button on the \"Create\" sub-tab of the \"Data Package\" tab to create a DSC Data Package Directory. You can then come back here and try adding your experiment file(s) again! <br><br>Exiting \"Add Experiment\" function now."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        

        # get tracker path
        trackerPath = os.path.join(dscDirPath,"heal-csv-experiment-tracker.csv")
        #parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Data Package Directory - Your Resource Tracker File lives here!')
        # resultsTrackerPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Results Tracker File to which you would like to add the Input Result Txt Data file(s)",
        #        (QtCore.QDir.homePath()), "CSV (*.csv *.tsv)")
               
        
        # if result tracker file selected, append the pd data object from the experiment file as a new row in the experiment tracker file
        # if doesn't exist, print error/info message and exit
        if trackerPath:

            #resultsTrackerPathStem = Path(resultsTrackerPath).stem

            if os.path.isfile(trackerPath):

            
                output_path = trackerPath
                all_df = pd.read_csv(output_path)
                #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
                all_df = pd.concat([all_df, collect_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
                all_df.sort_values(by = ["experimentIdNumber"], inplace=True)
                # drop any exact duplicate rows
                #all_df.drop_duplicates(inplace=True) # drop_duplicates does not work when df includes list vars
                # this current approach does not appear to be working at the moment
                print("all_df rows, with dupes: ", all_df.shape[0])
                all_df = all_df[-(all_df.astype('string').duplicated())]
                print("all_df rows, without dupes: ", all_df.shape[0])
            
                # before writing to file may want to check for duplicate resource IDs and if duplicate resource IDs, ensure that 
                # user wants to overwrite the earlier instance of the resource ID in the resource tracker - right now, dup entries 
                # for a resource are all kept as long as not exact dup (i.e. at least one thing has changed)

                all_df.to_csv(output_path, mode='w', header=True, index=False)
                #df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

                if invalidFiles:
                    messageText = "The contents of the Experiment file(s): <br><br>" + ', '.join(invalidFiles) + "<br><br>cannot be added to an Experiment Tracker file because they did not pass validation. Please review the validation errors printed above." 
                    errorFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(errorFormat.format(messageText))
            
                messageText = "The contents of the Experiment file(s): <br><br>" + ', '.join(validFiles) + "<br><br>were added as an experiment(s) to the Experiment Tracker file: <br><br>" + output_path
                errorFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
        
            else:
                messageText = "There is not a valid HEAL formatted experiment tracker file in the current working Data Package Directory."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
                return
  
    def clear_form(self):

        clearState = deepcopy(self.form.widget.state)
        #clearState = currentState.fromkeys(currentState, None)

        print("clearState before clear: ", clearState) # form state before clear

        for key, value in clearState.items():
            print(key, value)
            if type(value) is str:
                clearState[key] = ""
            if type(value) is list:
                clearState[key] = []

        print("clearState after clear: ", clearState) # form state totally cleared
        
        for key, value in clearState.items():
            print(key, value)
            if key in self.formDefaultState.keys():
                print("yes")
                clearState[key] = self.formDefaultState[key]
        
        print("clearState with default vals: ", clearState) # form state with default values added back in
        print(self.form.widget.state)
        print(self.form.widget.state.items())
        
        for key, value in self.form.widget.state.items():
            #self.form.widget.state[key] = clearState[key]
            print("key: ", key)
            print("value: ", value)

            self.form.widget.state = {
                key: clearState[key]
            } 

        #self.form.widget.state = deepcopy(clearState)
        print(self.form.widget.state)

        # if self.lstbox_view2.count() > 0:
        #     self.lstbox_view2.clear()
        #     self.get_items_list2()
        # else:
        #     if self.items2:
        #         self.items2 = []

        
        messageText = "<br>Your form was successfully cleared and you can start annotating a new experiment"
        saveFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(saveFormat.format(messageText))
        self.userMessageBox.moveCursor(QTextCursor.End)

        self.get_id()

        # messageText = "<br>NOTE: The Result ID in your form has been re-set to the default value of \n'result-1\n'. If you know which result IDs you've already used, you can change the Result ID in the cleared form manually by adding 1 to the max Result ID you've already used. To generate a unique Result ID automatically, click the Add DSC Package Directory button above the form - this will re-add your DSC Package Directory, search that directory for Result IDs already used, generate a unique Result ID by adding 1 to the max Result ID already in use, and add that Result ID value to the form for you."
        # saveFormat = '<span style="color:blue;">{}</span>'
        # self.userMessageBox.append(saveFormat.format(messageText)) 
        self.userMessageBox.moveCursor(QTextCursor.End)           

    def load_file(self):
        #_json_filter = 'json (*.json)'
        #f_name = QFileDialog.getOpenFileName(self, 'Load data', '', f'{_json_filter};;All (*)')
        print("in load_file fx")

        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Result Txt Data file you want to edit",
        #        (QtCore.QDir.homePath()), "Text (*.txt)")
        if self.mode == "edit":
            textBit = "edit"
            textButton = "\"Edit an existing experiment\""
        elif self.mode == "add-based-on":
            textBit = "base a new experiment upon"
            textButton = "\"Add a new experiment based on an existing experiment\""

        
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Experiment txt file you want to " + textBit,
            self.saveFolderPath, "Text (*.txt)")

        if not ifileName: 
            messageText = "<br>You have not selected a file to " + textBit + ". Close this form now. If you still want to " + textBit + " an existing experiment, Navigate to the \"Experiment Tracker\" tab >> \"Add Experiment\" sub-tab and click the " + textButton + " push-button."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText)) 
        else: 
            #self.editMode = True
            # if self.mode == "edit":         
            #     self.saveFilePath = ifileName
            #     print("setting saveFilePath to path of chosen file")
            
            #print("saveFilePath: ", self.saveFilePath)
            print(Path(ifileName).parent)
            print(Path(self.saveFolderPath))

            # add check on if filename starts with exp-trk-exp?
            if not Path(ifileName).stem.startswith("exp-trk-exp-"):
                messageText = "<br>The file you selected may not be an experiment txt file - an experiment txt file will have a name that starts with \"exp-trk-exp-\" followed by a number which is that experiment's ID number. You must select an experiment txt file that is in your working Data Package Directory to proceed. <br><br> To proceed, close this form and return to the main DSC Data Packaging Tool window."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            # add check on if valid exp-trk file?

            # if user selects a exp txt file that is not in the working data pkg dir, return w informative message
            if Path(self.saveFolderPath) != Path(ifileName).parent:
                messageText = "<br>You selected an experiment txt file that is not in your working Data Package Directory; You must select an experiment txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br> To proceed, close this form and return to the main DSC Data Packaging Tool window."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #self.saveFolderPath = Path(ifileName).parent
            print("saveFolderPath: ", self.saveFolderPath)
            
            with open(ifileName, 'r') as stream:
                data = load(stream)
                print(data)

            if self.mode == "add-based-on":
                based_on_annotation_id = data["experimentId"]


            if self.mode == "edit":         
                self.saveFilePath = ifileName # is this necessary?
                print("setting saveFilePath to path of chosen file")

                self.annotation_id = data["experimentId"]
                self.annotationIdNum = int(self.annotation_id.split("-")[1])
                self.annotationFileName = 'exp-trk-'+ self.annotation_id + '.txt'
                #self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

                archiveFileStartsWith = Path(ifileName).stem + "-"
                print("archiveFileStartsWith: ",archiveFileStartsWith)

                # make sure an archive folder exists, if not create it
                if not os.path.exists(os.path.join(self.saveFolderPath,"archive")):
                    os.makedirs(os.path.join(self.saveFolderPath,"archive"))
                    # if an archive folder does not yet exist prior to this, then this will 
                    # necessarily be the first time the user is editing an annotation file
                    self.annotationArchiveFileNameNumber = 1
                    #self.annotationArchiveFileName = 'exp-trk-'+ self.annotation_id + '-0' + '.txt'
                else: 
                    print("checking if at least one archived version/file for this annotation txt file already exists; getting next available archive id")
                    # check for files that start with stem of ifileName
                    # get the string that follows the last hyphen in the stem of those files, convert that string to number
                    # get highest number, add 1 to that number
                    self.annotationArchiveFileNameNumber = dsc_pkg_utils.get_id(self=self, prefix=archiveFileStartsWith, folderPath=os.path.join(self.saveFolderPath,"archive"), firstIdNum=1)
                
                #self.annotationArchiveFileName = 'exp-trk-'+ self.annotation_id + '-' + str(self.annotationArchiveFileNameNumber) + '.txt'    
                self.annotationArchiveFileName = archiveFileStartsWith + str(self.annotationArchiveFileNameNumber) + '.txt'    

                # move the experiment annotation file user opened for editing to archive folder
                os.rename(ifileName,os.path.join(self.saveFolderPath,"archive",self.annotationArchiveFileName))
                messageText = "<br>Your original experiment annotation file has been archived at:<br>" + os.path.join(self.saveFolderPath,"archive",self.annotationArchiveFileName) + "<br><br>"
                saveFormat = '<span style="color:blue;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))

            self.form.widget.state = data

            if self.mode == "add-based-on":
                self.get_id()
                messageText = "<br>Your new experiment has been initialized based on information you entered for " + based_on_annotation_id + "<br><br>"
                saveFormat = '<span style="color:blue;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))

            # if len(data["associatedFileDependsOn"]) > 2: 
            #     self.lstbox_view2.addItems(data["associatedFileDependsOn"])
            #     self.add_multi_depend()   
            # 
          

        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateExpWindow()
    window.show()
    sys.exit(app.exec_())