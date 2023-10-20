import sys
import os
from json import dumps, loads, load

from qtpy import QtWidgets

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

#from schema_results_tracker import schema_results_tracker
from schema_experiment_tracker import schema_experiment_tracker
from dsc_pkg_utils import qt_object_properties, get_multi_like_file_descriptions, get_exp_names
import pandas as pd

from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtGui import QTextCursor
import sys

from pathlib import Path


from layout_fileurladdwidget import ListboxWidget
import re
from copy import deepcopy

class ScrollAnnotateExpWindow(QtWidgets.QMainWindow):
    def __init__(self, workingDataPkgDirDisplay, workingDataPkgDir, mode = "add"):
        super().__init__()
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.workingDataPkgDir = workingDataPkgDir
        self.mode = mode
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
        self.formWidgetList[self.formWidgetNameList.index("experimentName")].on_changed.connect(self.check_exp_name_unique)
        
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

    def check_exp_name_unique(self):
        
        self.experimentNameList = []
        self.experimentNameList = get_exp_names(self=self) # gets self.experimentNameList

        print("self.experimentNameList: ",self.experimentNameList)
        currentExperimentName = self.formWidgetList[self.formWidgetNameList.index("experimentName")].text()

        if currentExperimentName in self.experimentNameList:
            messageText = "<br>You've used this experiment name before, and experiment name must be unique - Please enter a unique experiment name. Experiment names already in use include: <br><br>" + "<br>".join(self.experimentNameList)
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
        else:  
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
            messageText = "<br>Your experiment was successfully written at: " + self.saveFilePath + "<br><br>You'll want to head back to the \'Add Experiment\' tab and use the \'Add Experiment\' button to add this experiment file to your experiment tracker file! You can do this now, or later - You can add experiment files to an experiment tracker file one at a time, or you can add multiple experiment files all at once, so you may choose to create experiment files for several/all of your experiments and then add them in one go to your experiment tracker file."
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            self.userMessageBox.moveCursor(QTextCursor.End)

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

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Result Txt Data file you want to edit",
               self.saveFolderPath, "Text (*.txt)")

        if not ifileName: 
            messageText = "<br>You have not selected a file; returning."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText)) 
        else: 
            #self.editMode = True
                     
            self.saveFilePath = ifileName
            print("saveFilePath: ", self.saveFilePath)
            print(Path(ifileName).parent)
            print(Path(self.saveFolderPath))

            # if user selects a result txt file that is not in the working data pkg dir, return w informative message
            if Path(self.saveFolderPath) != Path(ifileName).parent:
                messageText = "<br>You selected an experiment txt file that is not in your working Data Package Directory; You must select an experiment txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br> To proceed, close this form and return to the main DSC Data Packaging Tool window."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #self.saveFolderPath = Path(ifileName).parent
            print("saveFolderPath: ", self.saveFolderPath)
            
            with open(ifileName, 'r') as stream:
                data = load(stream)

            self.annotation_id = data["experimentId"]
            self.annotationIdNum = int(self.annotation_id.split("-")[1])
            self.annotationFileName = 'exp-trk-'+ self.annotation_id + '.txt'
            #self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

            # make sure an archive folder exists, if not create it
            if not os.path.exists(os.path.join(self.saveFolderPath,"archive")):
                os.makedirs(os.path.join(self.saveFolderPath,"archive"))

            # move the experiment annotation file user opened for editing to archive folder
            os.rename(ifileName,os.path.join(self.saveFolderPath,"archive",self.annotationFileName))
            messageText = "<br>Your original experiment annotation file has been archived at:<br>" + os.path.join(self.saveFolderPath,"archive",self.annotationFileName) + "<br><br>"
            saveFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

            self.form.widget.state = data

            # if len(data["associatedFileDependsOn"]) > 2: 
            #     self.lstbox_view2.addItems(data["associatedFileDependsOn"])
            #     self.add_multi_depend()         

        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateExpWindow()
    window.show()
    sys.exit(app.exec_())