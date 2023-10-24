import sys
import os
from json import dumps, loads, load

from qtpy import QtWidgets

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

#from schema_resource_tracker import schema_resource_tracker
#from form_schema_resource_tracker import form_schema_resource_tracker
from schema_resource_tracker import form_schema_resource_tracker, schema_resource_tracker
from dsc_pkg_utils import qt_object_properties, get_multi_like_file_descriptions
import pandas as pd
import dsc_pkg_utils

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

class ScrollAnnotateResourceWindow(QtWidgets.QMainWindow):
    def __init__(self, workingDataPkgDirDisplay, workingDataPkgDir, mode = "add", *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.setWindowTitle("Annotate Resource")
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.workingDataPkgDir = workingDataPkgDir
        self.initUI()
        #self.load_file()

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
        #self.schema = form_schema_resource_tracker
        self.schema = schema_resource_tracker

        self.experimentNameList = []
        self.experimentNameList = dsc_pkg_utils.get_exp_names(self=self) # gets self.experimentNameList

        print("self.experimentNameList: ",self.experimentNameList)
        
        if self.experimentNameList:
            #self.schema = self.add_exp_names_to_schema() # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList
            self.schema = dsc_pkg_utils.add_exp_names_to_schema(self=self) # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList

        self.ui_schema = {}
        
        self.builder = WidgetBuilder(self.schema)
        self.form = self.builder.create_form(self.ui_schema)
        
        self.formDefaultState = {
            "resourceId": "resource-1",
            "experimentNameBelongsTo": "default-experiment-name",
            #"expBelongsTo": "exp-999",
            "accessDate": "2099-01-01"
        }

        self.form.widget.state = deepcopy(self.formDefaultState)
      
        # # create 'add dsc data pkg directory' button
        # self.buttonAddDir = QtWidgets.QPushButton(text="Add DSC Package Directory",parent=self)
        # self.buttonAddDir.clicked.connect(self.add_dir)

        # self.buttonAddDir.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.buttonAddDir.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
                

        # create save button
        self.buttonSaveResource = QtWidgets.QPushButton(text="Save resource",parent=self)
        self.buttonSaveResource.clicked.connect(self.save_resource)

        self.buttonSaveResource.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonSaveResource.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
        

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

        # create button to add multiple like resources
        self.buttonAddMultiResource = QtWidgets.QPushButton(text="Add Multiple \'like\' Resources",parent=self)
        self.buttonAddMultiResource.clicked.connect(self.add_multi_resource)
        self.labelAddMultiResource = QtWidgets.QLabel(text="To add multiple 'like' resources, <b>drag and drop file paths right here</b>. If you are annotating a single file, you can drag and drop it here or browse to the file using the Resource File Path field in the form below.",parent=self)
        self.labelApplyNameConvention = QtWidgets.QLabel(text="To apply a naming convention when adding multiple 'like' resources that share a naming convention, <b>add your naming convention in the Name Convention field in the form below</b>, then come back and <b>click the Apply Name Convention button right here</b> to apply. This will autogenerate a minimal description based on the naming convention for each of your 'like' files." + "\n\n" + "e.g." + "\n" + "Name Convention: subject_{subject ID}_day_{date of data collection in YYYYMMDD})" + "\n" + "Example File Name: subject_A1_day_20230607)" + "\n" + "Autogenerated File Description: subject ID: A1, date of data collection in YYYYMMDD: 20230607)",parent=self)

        self.labelAddMultiResource.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.labelApplyNameConvention.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )

        self.labelAddMultiResource.setWordWrap(True)
        self.labelApplyNameConvention.setWordWrap(True)
        
        # create button to apply naming convention for multiple like resources
        self.buttonApplyNameConvention = QtWidgets.QPushButton(text="Apply Name Convention",parent=self)
        self.buttonApplyNameConvention.clicked.connect(self.apply_name_convention)
                        
        # create drag and drop window for multiple like file addition
        self.lstbox_view = ListboxWidget(self)
        self.lwModel = self.lstbox_view.model()
        self.items = []
        self.programmaticListUpdate = False
        self.lwModel.rowsInserted.connect(self.get_items_list)
        self.lwModel.rowsRemoved.connect(self.get_items_list)

        # create button to add multiple file dependencies addition
        self.buttonAddMultiDepend = QtWidgets.QPushButton(text="Add Multiple Resource Dependencies",parent=self)
        self.buttonAddMultiDepend.clicked.connect(self.add_multi_depend)
        self.labelAddMultiDepend = QtWidgets.QLabel(text="To add multiple file dependencies for your resource, <b>drag and drop file paths right here</b>. If your resource has one or just a few dependencies, you can drag and drop them here or browse to each dependency (one dependency at a time) using the Associated Files/Dependencies field in the form below.",parent=self)
        
        self.labelAddMultiDepend.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )

        self.labelAddMultiDepend.setWordWrap(True)

        # create drag and drop window for multiple file dependencies addition
        self.lstbox_view2 = ListboxWidget(self)
        self.lwModel2 = self.lstbox_view2.model()
        self.items2 = []
        self.programmaticListUpdate2 = False
        self.lwModel2.rowsInserted.connect(self.get_items_list2)
        self.lwModel2.rowsRemoved.connect(self.get_items_list2)
       
        ################################## Apply some initializing and maintenance functions

        # initialize tool tip for each form field based on the description text for the corresponding schema property
        self.add_tooltip()
        self.add_priority_highlight_and_hide()
        self.add_dir()
        if self.mode == "add":
            self.get_id()
        #self.add_priority_highlight()
        #self.initial_hide()
        self.popFormField = []
        self.editSingle = False

        # check for emptyp tooltip content whenever form changes and replace empty tooltip with original tooltip content
        # (only relevant for fields with in situ validation - i.e. string must conform to a pattern - as pyqtschema will replace the 
        # tooltip content with some error content, then replace the content with empty string once the error is cleared - this check will
        # restore the original tooltip content - for efficiency, may want to only run this when a widget that can have validation 
        # errors changes - #TODO)
        self.form.widget.on_changed.connect(self.check_tooltip)
        self.formWidgetList[self.formWidgetNameList.index("category")].on_changed.connect(self.conditional_fields)
        self.formWidgetList[self.formWidgetNameList.index("access")].on_changed.connect(self.conditional_fields)
        self.formWidgetList[self.formWidgetNameList.index("descriptionFileNameConvention")].on_changed.connect(self.conditional_highlight_apply_convention)
        self.formWidgetList[self.formWidgetNameList.index("categorySubMetadata")].on_changed.connect(self.conditional_fields)
        self.formWidgetList[self.formWidgetNameList.index("path")].on_changed.connect(self.conditional_fields)
        
        #self.form.widget.on_changed.connect(self.check_priority_highlight)
        
        ################################## Finished creating component widgets
        #self.mfilehbox.addWidget(self.buttonAddMultiResource)
        #self.mfilehbox.addWidget(self.buttonApplyNameConvention)

        self.vbox.addWidget(self.buttonAddDir)
        self.vbox.addWidget(self.buttonSaveResource)
        self.vbox.addWidget(self.buttonClearForm)
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
        
        self.vbox.addWidget(self.buttonAddMultiResource)
        
        #self.vbox.addLayout(self.mfilehbox)
        self.vbox.addWidget(self.labelAddMultiResource)
        self.vbox.addWidget(self.lstbox_view)
        self.vbox.addWidget(self.labelApplyNameConvention)
        self.vbox.addWidget(self.buttonApplyNameConvention)

        self.vbox.addWidget(self.buttonAddMultiDepend)
        self.vbox.addWidget(self.labelAddMultiDepend)
        self.vbox.addWidget(self.lstbox_view2)

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
        #if self.editState: 
        #    self.load_file

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

        self.labelAddMultiResource.hide()
        self.lstbox_view.hide()
        self.labelApplyNameConvention.hide()
        self.buttonApplyNameConvention.hide()
        self.labelAddMultiDepend.hide()
        self.lstbox_view2.hide()

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
    
    def conditional_fields(self, changedFieldName):

        #if changedFieldName == "category":

        # reminder to add dd if tabular data; reminder to add result tracker if multi-result 

        if self.form.widget.state["category"] == "tabular-data":
            messageText = "<br>You have indicated your resource is a tabular data resource. Please ensure that you add a data dictionary for this tabular data resource in the Associated Data Dictionary field in the form below. A HEAL formatted data dictionary is highly preferred. If you don't already have a HEAL formatted data dictionary, you can easily create one directly from your tabular data file by visiting the Data Dictionary tab of the DSC Packaging Desktop application. You can leave this form open, visit the Data Dictionary tab to create and save your HEAL formatted data dictionary, and then return to this form to add the data dictionary you created."
            errorFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))

        if self.form.widget.state["category"] == "multi-result":
            messageText = "<br>You have indicated your resource is a multi-result resource. Please ensure that you add a result tracker for this multi-result resource in the Associated Result Tracker field in the form below. A result tracker is a HEAL formatted file to track all results in a multi-result file, along with the data and other supporting files that underly each result. If you don't already have a HEAL formatted result tracker, you can easily create one by visiting the Result Tracker tab of the DSC Packaging Desktop application. You can leave this form open, visit the Result Tracker tab to create and save your HEAL formatted result tracker, and then return to this form to add the result tracker you created."
            errorFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))

        if self.form.widget.state["category"] == "metadata":
            if self.form.widget.state["categorySubMetadata"] == "heal-formatted-results-tracker":
                messageText = "<br>You have indicated your resource is a HEAL formatted Results Tracker. The Associated Files/Dependencies field in this form has been hidden from view because this field cannot be used to add file dependencies for a Results Tracker file. If your Result Tracker is correctly formatted, and you have provided file dependencies for each result listed in the results tracker, file dependencies will be pulled in directly from the Results Tracker."
                errorFormat = '<span style="color:blue;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))

                if not self.form.widget.state["path"]:
                    messageText = "<br>Please use the Resource File Path field in the form to browse to your Results Tracker file."
                    errorFormat = '<span style="color:blue;">{}</span>'
                    self.userMessageBox.append(errorFormat.format(messageText))

                if self.form.widget.state["path"]:
                    pathStem = Path(self.form.widget.state["path"]).stem
                    if not pathStem.startswith("heal-csv-results-tracker"):
                        messageText = "<br>The resource file path you have added to the Resource File Path field in the form does not appear to be a HEAL formatted results tracker, or the tracker has been re-named. Please ensure that you have added a HEAL formatted Results Tracker to the Resource File Path field in the form, and that the Results tracker name follows the naming convention: heal-csv-results-tracker-(name of multi-result file with which the results tracker is associated)."
                        errorFormat = '<span style="color:red;">{}</span>'
                        self.userMessageBox.append(errorFormat.format(messageText))
                    else: 
                        # formally validate the results tracker here?
                        self.popFormField = []

                        messageText = "<br>The resource file path you have added to the Resource File Path field in the form appears to be a HEAL formatted results tracker. Attempting to extract file dependencies for each result in the results tracker now."
                        errorFormat = '<span style="color:green;">{}</span>'
                        self.userMessageBox.append(errorFormat.format(messageText))
                       
                        resultsTrk = pd.read_csv(self.form.widget.state["path"])
                        resultIds = resultsTrk["resultId"].tolist()

                        if resultIds:
                            resultIdDependencies = resultsTrk["associatedFileDependsOn"].tolist()

                            
                            
                            popFormField = [{"resultId": rId, "resultIdDependsOn": rIdD.strip("][").split(", ")} for rId,rIdD in zip(resultIds,resultIdDependencies)]
                            print("popFormField: ", popFormField)

                            messageText = "<br>Extracted file dependencies for each result in the results tracker are as follows:<br><br>"
                            #errorFormat = '<span style="color:green;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))
                            self.userMessageBox.append(messageText)

                            emptyDependencies = []
                            formatDependencies = []
                            for i, list_item in enumerate(popFormField):
                                self.userMessageBox.append(f"{i + 1}. ")
                                for j, key in enumerate(list_item.keys()):
                                    self.userMessageBox.append(f"{key}:{list_item[key]}{'' if j == len(list_item) - 1 else ', '}")
                                    if key == "resultId":
                                        resultId = list_item[key]
                                    if key == "resultIdDependsOn":
                                        if not list_item[key]:
                                            emptyDependencies.append(resultId)
                                            print("emptyDependencies: ",emptyDependencies)
                                            formatDependencies.append([])
                                        else:
                                            formatDependencies.append([item.replace("'", '') for item in list_item[key]])
                                            
                                self.userMessageBox.append("")

                            self.popFormField = [{"resultId": rId, "resultIdDependsOn": rIdD} for rId,rIdD in zip(resultIds,formatDependencies)]
                            print("popFormField_format: ", self.popFormField)

                            if emptyDependencies:
                                messageText = "<br>The following result IDs listed in the Results Tracker did not have any file dependencies listed:<br>" + ", ".join(emptyDependencies) + "<br><br>Please review your results tracker and add file dependencies for each result as appropriate, then come back and re-add the results tracker as a resource.<br><br>"
                                errorFormat = '<span style="color:red;">{}</span>'
                                self.userMessageBox.append(errorFormat.format(messageText))

                            #self.form.widget.state = {
                            #    "associatedFileResultsDependOn": popFormField
                            #}
                        
                        else: 
                            messageText = "<br>There do not appear to be any results listed in the Results Tracker. Please add at least one result to your Results Tracker by navigating to the Add Results sub-tab of the Results Tracker tab. If you have already annotated your result(s), use the Add result or Auto-add result button to add your result files to your Result Tracker. If you need to annotate your result(s), start by clicking the Annotate Result button, fill out the brief form that appears to annotate your result(s), use the Add or Auto-add Result button(s) to add your result file(s) to your Results Tracker, then come back here to re-add your Results Tracker as a resource.<br>"
                            errorFormat = '<span style="color:red;">{}</span>'
                            self.userMessageBox.append(errorFormat.format(messageText))
                        



        # this is an inefficient way to make sure previously unhidden fields get hidden again if user changes the category
        # should really save the last chosen state and be selective about re-hiding the ones that were revealed due to the
        # previous selection

        ################### hide fields that were revealed due to previous selection

        if self.form.widget.state["category"] != "tabular-data":
            self.toggle_widgets(keyText = "data", desiredToggleState = "hide")
            self.toggle_widgets(keyText = "tabular data", desiredToggleState = "hide")
            # delete contents of conditional fields if any added
            self.form.widget.state = {
                "descriptionRow": "",
                "associatedFileDataDict": []
            } 
            
        if self.form.widget.state["category"] != "non-tabular-data":
            self.toggle_widgets(keyText = "data", desiredToggleState = "hide")
            
        if self.form.widget.state["category"] not in ["tabular-data","non-tabular-data"]:
            # delete contents of conditional fields if any added
            self.form.widget.state = {
                    "categorySubData": "",
                    "associatedFileProtocol": []
                } 
        
        if self.form.widget.state["category"] != "metadata":
            self.toggle_widgets(keyText = "metadata", desiredToggleState = "hide")
            # delete contents of conditional fields if any added
            self.form.widget.state = {
                    "categorySubMetadata": ""
                } 

        if self.form.widget.state["category"] not in ["single-result","multi-result"]:
            self.toggle_widgets(keyText = "results", desiredToggleState = "hide")
            # delete contents of conditional fields if any added
            self.form.widget.state = {
                    "categorySubResults": ""
                } 

        if self.form.widget.state["category"] != "multi-result":
            self.toggle_widgets(keyText = "multi-result", desiredToggleState = "hide")
            self.toggle_widgets(keyText = "not multi-result", desiredToggleState = "show")
            self.form.widget.state = {
                    "associatedFileResultsTracker": []
                } 

        if self.form.widget.state["category"] == "metadata":
            if self.form.widget.state["categorySubMetadata"] != "heal-formatted-results-tracker":
                self.toggle_widgets(keyText = "not results-tracker", desiredToggleState = "show")
                # clear associatedFileResultsDependOn field (not sure the format for this, is it a list of lists?)
                self.popFormField = []

        if self.form.widget.state["category"] != "metadata":
            #if self.form.widget.state["categorySubMetadata"] == "heal-formatted-results-tracker":
                self.toggle_widgets(keyText = "not results-tracker", desiredToggleState = "show")
                self.form.widget.state = {
                    "categorySubMetadata": ""
                } 
                self.popFormField = []

        ################### show field appropriate to current selection
            
        if self.form.widget.state["category"] == "tabular-data":
            self.toggle_widgets(keyText = "data", desiredToggleState = "show")
            self.toggle_widgets(keyText = "tabular data", desiredToggleState = "show")
           
        if self.form.widget.state["category"] == "non-tabular-data":
            self.toggle_widgets(keyText = "data", desiredToggleState = "show")
           
        if self.form.widget.state["category"] == "metadata":
            self.toggle_widgets(keyText = "metadata", desiredToggleState = "show")

        if self.form.widget.state["category"] in ["single-result","multi-result"]:
            self.toggle_widgets(keyText = "results", desiredToggleState = "show")

        if self.form.widget.state["category"] == "multi-result":
            self.toggle_widgets(keyText = "multi-result", desiredToggleState = "show")
            self.toggle_widgets(keyText = "not multi-result", desiredToggleState = "hide")

        if self.form.widget.state["category"] == "metadata":
            if self.form.widget.state["categorySubMetadata"] == "heal-formatted-results-tracker":
                self.toggle_widgets(keyText = "not results-tracker", desiredToggleState = "hide")

        #if changedFieldName == "access":

        if "temporary-private" in self.form.widget.state["access"]:
            self.toggle_widgets(keyText = "temporary private", desiredToggleState = "show")
            
            messageText = "<br>You have indicated your resource will be temporarily held as private. Please 1) use the Access field to indicate the access level at which you'll set this resource once the temporary private access setting expires (either public access, or restricted access), and 2) use the Access Date field to indicate the date at which the temporary private access level is expected to expire (You will not be held to this date - Estimated dates are appreciated)."
            errorFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))

        else:
            self.toggle_widgets(keyText = "temporary private", desiredToggleState = "hide") 

            self.form.widget.state = {
                "accessDate": self.formDefaultState["accessDate"]
            } 
                
    def conditional_highlight_apply_convention(self):

        if self.form.widget.state["descriptionFileNameConvention"]:
            self.buttonApplyNameConvention.setStyleSheet("background-color : rgba(0,125,0,50)")
        else:
            self.buttonApplyNameConvention.setStyleSheet("")
            
            self.form.widget.state = {
                "descriptionFile": ""
            }

            self.itemsDescriptionList = []

    def add_dir(self):
        
        #self.saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new resource will be saved there!')
        self.saveFolderPath = self.workingDataPkgDir

    def get_id(self):

        if self.saveFolderPath:

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

            messageText = "<br>Based on other resources already saved in your DSC Package directory, your new resource will be saved with the unique ID: " + self.resource_id + "<br>Resource ID has been added to the resource form."
            messageText = messageText + "<br>Your new resource file will be saved in your DSC Package directory as: " + self.saveFilePath + "<br><br>"
            self.userMessageBox.append(messageText)
            #self.userMessageBox.moveCursor(QTextCursor.End)

            # if there's not a resource tracker template already in the directory they added
            # let them proceed but provide an informative warning
            if not os.path.isfile(os.path.join(self.saveFolderPath,"heal-csv-resource-tracker.csv")):
                messageText = "<br>Warning: It looks like there is no HEAL formatted resource tracker in the directory you selected. Are you sure you selected a directory that is a DSC package directory? If you have not already created a DSC package directory, you can do so now by navigating to the DSC Package tab in the application, and clicking on the Create sub-tab. This will create a directory called \n'dsc-pkg\n' which will have a HEAL formatted resource tracker file inside. Once you've done that please return here and add this directory before proceeding to annotate your resource files."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))

            self.form.widget.state = {
                "resourceId": self.resource_id
            }

        else:
            messageText = "<br>Please set your working DSC Data Package Directory to proceed."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        
    def get_items_list(self):
        #item = QListWidgetItem(self.lstbox_view.currentItem())
        #print(item.text())
        if self.programmaticListUpdate:
            self.programmaticListUpdate = False
            return

        lw = self.lstbox_view
        
        oldLength = None
        if self.items:
            oldLength = len(self.items)
            oldItems = self.items

        self.items = [lw.item(x).text() for x in range(lw.count())]
        print(self.items)

        refactorItems = []
        for i in self.items:
            print(i)
            if os.path.isdir(i):
                #self.programmaticListUpdate = True
                myFiles = [os.path.join(i,f) for f in os.listdir(i) if os.path.isfile(os.path.join(i,f))]
                print(myFiles)
                refactorItems.extend(myFiles)
            else:
                refactorItems.append(i)

        if self.items != refactorItems:
            self.programmaticListUpdate = True

            self.items = refactorItems
            self.lstbox_view.clear()
            self.lstbox_view.addItems(self.items)

        newLength = len(self.items)
        print(self.items)  
        #print(type(self.items)) 
        print(len(self.items))

        if self.items:
            updatePath = self.items[0]
            updateAssocFileMultiLike = self.items
        else:
            updatePath = ""
            updateAssocFileMultiLike = []

        self.form.widget.state = {
            "path": updatePath,
            "associatedFileMultiLikeFiles": updateAssocFileMultiLike
        } 

        
        if len(self.items) > 1:
            print("show")
            indices = [i for i, x in enumerate(self.priorityContentList) if ("multiple like resource" in x) and ("permanent hide" not in x)]
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

                labelW.show()
                fieldW.show()

            self.labelApplyNameConvention.show()
            self.buttonApplyNameConvention.show()

        if oldLength:
            if ((oldLength > 1) and (newLength <= 1)):
                print("hide")
                indices = [i for i, x in enumerate(self.priorityContentList) if "multiple like resource" in x]
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

                    labelW.hide()
                    fieldW.hide()
                    # should also probably delete the contents of these folders?

                self.labelApplyNameConvention.hide()
                self.buttonApplyNameConvention.hide()
                
    def get_items_list2(self):
        #item = QListWidgetItem(self.lstbox_view.currentItem())
        #print(item.text())
        if self.programmaticListUpdate2:
            self.programmaticListUpdate2 = False
            return

        lw = self.lstbox_view2
        
        oldLength = None
        if self.items2:
            oldLength = len(self.items2)
            oldItems = self.items2

        self.items2 = [lw.item(x).text() for x in range(lw.count())]
        print(self.items2)

        refactorItems = []
        for i in self.items2:
            print(i)
            if os.path.isdir(i):
                #self.programmaticListUpdate = True
                myFiles = [os.path.join(i,f) for f in os.listdir(i) if os.path.isfile(os.path.join(i,f))]
                print(myFiles)
                refactorItems.extend(myFiles)
            else:
                refactorItems.append(i)

        if self.items2 != refactorItems:
            self.programmaticListUpdate2 = True

            self.items2 = refactorItems
            self.lstbox_view2.clear()
            self.lstbox_view2.addItems(self.items2)

        newLength = len(self.items2)
        print(self.items2)  
        #print(type(self.items)) 
        print(len(self.items2))

        if self.items2:
            #updatePath = self.items2[0]
            updateAssocFileMultiDepend = self.items2
        else:
            #updatePath = ""
            updateAssocFileMultiDepend = []

        self.form.widget.state = {
            #"path": updatePath,
            "associatedFileDependsOn": updateAssocFileMultiDepend
        } 

        
    
        if oldLength:
            if ((oldLength > 0) and (newLength == 0)):
                print("hide")
                
                self.labelAddMultiDepend.hide()
                self.lstbox_view2.hide()
                
    def conditional_priority_highlight(self, priorityText, fontColor):

        # not in use? confirm and delete
        
        indices = [i for i, x in enumerate(self.priorityContentList) if x == priorityText]

        for i in indices:
            labelW = self.formLabelWidgetList[i]
            labelWType = self.formLabelWidgetTypeList[i]
            labelWText = self.formLabelWidgetTextList[i]

            fColor = fontColor

            if (labelWType == "label"):
                labelW.setText('<font color = ' + fColor + '>' + labelW.text() + '</font>')
            if (labelWType == "groupbox"):
                labelW.setStyleSheet('QGroupBox  {color: ' + fColor + ';}')

    def add_multi_resource(self):

        if ((self.lstbox_view.isHidden()) and (self.labelAddMultiResource.isHidden())):
            self.lstbox_view.show()
            self.labelAddMultiResource.show()
        else:
            self.lstbox_view.hide()
            self.labelAddMultiResource.hide()

    def add_multi_depend(self):

        if ((self.lstbox_view2.isHidden()) and (self.labelAddMultiDepend.isHidden())):
            self.lstbox_view2.show()
            self.labelAddMultiDepend.show()
        else:
            self.lstbox_view2.hide()
            self.labelAddMultiDepend.hide()

    def apply_name_convention(self):
        # have to do this after add_tooltip because these items are defined in that function - may want to change that at some point
        # get the name convention widget 
        # if the contents of the name convention widget
        self.nameConventionWidgetIdx = self.formWidgetNameList.index("descriptionFileNameConvention")
        self.nameConventionWidget = self.formWidgetList[self.nameConventionWidgetIdx] 
        print("my state: ", self.nameConventionWidget.state)
        self.nameConvention = self.nameConventionWidget.state

        try:
            #found = re.search('{(.+?)}', self.nameConvention).group(1)
            nameConventionExplanatoryList = re.findall('{(.+?)}', self.nameConvention)
            print(nameConventionExplanatoryList)
        except AttributeError:
            # {} not found in the original string
            #nameConventionExplanatoryList = '' # apply your error handling
            print('you have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}')
            messageText = "<br>You have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}"
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        if not nameConventionExplanatoryList:
            messageText = "<br>You have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}"
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # check if specified name convention includes directory structure (if so should provide full path, including file extension when specifying file name convention)
        s = rf"{self.nameConvention}"
        s1 = s.split('/')
        s2 = s.split('\\')
        print("forward slash split: ", s1, "back slash split: ", s2)

        if ((len(s1) > 1) or (len(s2) > 1)):
            keepFullPath = True
            messageText = "<br> Because the file name convention you entered contains either forward or back slashes, the file name convention you entered will be applied to the full path of each file in the set of multiple 'like' resources you added to the file drop box. When directory structure is used as part of the file naming convention, please specify the name convention including the full path and the file extension in the file name convention string you provide in the form."  
            self.userMessageBox.append(messageText)
            self.scrollScrollArea(topOrBottom = "top")
        else:
            messageText = "<br> Because the file name convention you entered does not contain either forward or back slashes, the file name convention you entered will be applied to the stem of the full path of each file in the set of multiple 'like' resources you added to the file drop box. When directory structure is NOT used as part of the file naming convention, please specify the name convention including just the filename excluding the file extension in the file name convention string you provide in the form."  
            self.userMessageBox.append(messageText)
            self.scrollScrollArea(topOrBottom = "top")
            keepFullPath = False

        if not keepFullPath:
            # get just file stems from full path, this also removes file extensions
            if self.items:
                self.fileStemList = [Path(p).stem for p in self.items]
            else:
                self.fileStemList = [Path(self.form.widget.state["path"]).stem]
        else:
            if self.items:
                self.fileStemList = [p for p in self.items]
            else:
                self.fileStemList = [self.form.widget.state["path"]]
            

        self.itemsDescriptionList = []
        self.itemsDescriptionMessagesOut = []

        self.itemsDescriptionList, itemsDescriptionMessagesOut = get_multi_like_file_descriptions(self.nameConvention, self.fileStemList)

        if self.itemsDescriptionList:
            print(self.itemsDescriptionList)
            
            if all(self.itemsDescriptionList):
                self.form.widget.state = {
                    "descriptionFile": self.itemsDescriptionList[0]
                } 

                applyConvention = "successful. Please see the Resource File Description field in the form below to see the file description assigned to the first file in your set of multiple 'like' resource files"
                textColor = "green"
            else: 
                applyConvention = "unsuccessful. Examine any errors the attempt produced (red text below), ensure that you are following the required conventions for specifying your naming convention, and come back and try again"
                textColor = "red"
            
            messageText = "<br>Your attempt to apply a name convention for your set of 'like' resource files was " + applyConvention + "."  
            textColorFormat = '<span style="color:' + textColor + ';">{}</span>'
            self.userMessageBox.append(textColorFormat.format(messageText))
            self.scrollScrollArea(topOrBottom = "top")

        if itemsDescriptionMessagesOut:
            print(itemsDescriptionMessagesOut)
            
            itemsDescriptionMessagesOut = [''.join(list(m)) for m in itemsDescriptionMessagesOut]
            print(itemsDescriptionMessagesOut)

            messageText = "<br> Your attempt to apply a name convention for your set of 'like' resource files produced the following errors: <br>" + '\n'.join(itemsDescriptionMessagesOut)  
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            self.scrollScrollArea(topOrBottom = "top")

    def save_resource(self):
        
        # this should no longer be necessary as the form will only be opened if a valid working data pkg dir has been set by the user and the path has been passed as a string to the form widget
        # check that a dsc data package dir has been added - this is the save folder - if not exit with informative error
        if not self.saveFolderPath:
            messageText = "<br>You must add a DSC Data Package Directory before saving your resource file. Please add a DSC Data Package Directory and then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # check that file path and at least a minimal description has been added to the form 
        # if not exit with informative error
        if not ((self.form.widget.state["path"]) and (self.form.widget.state["description"])):
            messageText = "<br>You must add a resource file path and at least a minimal description of your resource to your resource file form before saving your resource file. Please add a resource file path either by browsing to the file path using the Resource File Path field in the form, or by dragging and dropping the file path for your resource file (or multiple file paths if you are annotating multiple 'like' resources at once) in the drag and drop box above the form (open this drag and drop box by clicking on the Add Multiple 'like' Resources button above the form), and add at least a minimal description of your resource (or set of 'like' resources) in the Resource Description field in the form. Then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        
        # check if user has modified the resource id from the one that was autogenerated when adding dsc data dir for saving
        # this may happen if for example a user annotates a resource using the autogenerated resource id, then wants to keep 
        # going using the same form window instance, modify the contents to annotate a new resource (perhaps one with some 
        # form fields that will be the same), and save again with a new resource id - in this case the user can modify the 
        # resource id manually, incrementing the id number by one - if resource id modified, updated it in memory and regenerate
        # the save file name, save file path, and resource id number
        if self.form.widget.state["resourceId"] != self.resource_id:
            
            self.resource_id = self.form.widget.state["resourceId"]
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
                self.itemsDescriptionList = [self.form.widget.state["descriptionFile"]]
        else:
            self.resource_id_list = [self.resource_id]
            self.resourceFileNameList = [self.resourceFileName]
            self.saveFilePathList = [self.saveFilePath]
            self.items = [self.form.widget.state["path"]]
            self.itemsDescriptionList = [self.form.widget.state["descriptionFile"]]
                
        if self.editSingle:
            self.resource_id_list = [self.resource_id]
            self.resourceFileNameList = [self.resourceFileName]
            self.saveFilePathList = [self.saveFilePath]
            self.items = [self.form.widget.state["path"]]
            self.itemsDescriptionList = [self.form.widget.state["descriptionFile"]]            
        
        #messageText = ""

        successResIdList = []
        successSaveFilePathList = []
        failResIdList = []
        failSaveFilePathList = []
        resourceList = []

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

        # if any of the potential resource id/resource id annotation files already exist - exit with informative message about checking/updating resource id        
        if failResIdList:
            #print("something went wrong - check the resource id in your form - do you already have a resource file saved for a resource with this resource id? if not, did you add multiple like resource files? resource ids will be autogenerated for all of the resource files you added - IDs will be generated by adding 1 to the resource id in your form for each file in turn - do you already have a resource file saved for a resource with one of the resource ids that may have been autogenerated based on this approach? the safest thing to do is to check the resource files you have saved in your dsc package folder, find the highest resource id number for which you have created/saved a resource file, and enter your resource id in the form as having an id number one higher than the max resource id number you identified - then try saving again - if you add your dsc package directory using the push button at the top of the form window, a resource id will be autogenerated for you using this approach automatically.")
            messageText = "<br>WARNING: Your resource(s) were not written to file because something went wrong - Check the Resource ID in your form - Do you already have a resource file saved for a resource with this resource id? if not, did you add multiple like resource files? Resource IDs will be autogenerated for all of the resource files you added - IDs will be generated by adding 1 to the resource id in your form for each file in turn - do you already have a resource file saved for a resource with one of the resource ids that may have been autogenerated based on this approach? the safest thing to do is to check the resource files you have saved in your dsc package folder, find the highest resource id number for which you have created/saved a resource file, and enter your resource id in the form as having an id number one higher than the max resource id number you identified - then try saving again."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        else:
            #print(self.form.widget.state)
            resource = deepcopy(self.form.widget.state)

            resourceDepend = resource["associatedFileDataDict"] + resource["associatedFileProtocol"] + resource["associatedFileResultsTracker"] + resource["associatedFileDependsOn"]
            
            if self.popFormField:
                resource["associatedFileResultsDependOn"] = self.popFormField

                for item in resource["associatedFileResultsDependOn"]:
                    resourceDepend.extend(item["resultIdDependsOn"])

 
            for idx, p in enumerate(self.saveFilePathList):
                    
                #resource = self.form.widget.state
                currentResource = deepcopy(resource)
                    
                currentResource["resourceId"] = self.resource_id_list[idx]
                currentResource["path"] = self.items[idx]
                currentResource["descriptionFile"] = self.itemsDescriptionList[idx]
                
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
            messageText = "<br>Your resource " + myString1 + " successfully written at: " + myString2 + "<br><br>You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

            messageText = "<br>NOTE: You added the following files as associated with or dependencies for your resource(s) - <b>If you are annotating wholistically</b>, please ensure that you annotate each of these files and add each of them as their own resource to the resource tracker. <b>If you are annotating minimally</b>, do the same, but only for the files that you will share in a public repository: <br><br>" + "<br>".join(resourceDepend) + "<br><br>"
            saveFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

            self.userMessageBox.moveCursor(QTextCursor.End)

            if self.form.widget.state["category"] == "tabular-data":
                if not self.form.widget.state["associatedFileDataDict"]:

                    messageText = "<br>WARNING: You annotated a tabular data resource and did not include a data dictionary for this tabular data resource. If you don't already have a data dictionary, please visit the Data Dictionary tab to create a data dictionary for this resource. You can easily and automatically create a data dictionary using only your tabular data file. Once you have a data dictionary, you can come back here and edit this form to add your data dictionary and save again. You may need to delete the file that was just saved before saving again, as overwriting is not currently allowed." + "\n\n"
                    saveFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    self.userMessageBox.moveCursor(QTextCursor.End)

            if "temporary-private" in self.form.widget.state["access"]:
                if not any(map(lambda v: v in self.form.widget.state["access"], ["public","restricted-access"])):

                    messageText = "<br>WARNING: You indicated that this resource has an access level of \n'temporary-private\n' but did not indicate whether the access level would transition to \n'public\n' or to \n'restricted-access\n' once the temporary-private status expires. Please return to the form to indicate what the final access level of this resource will be by adding another value to the Access field on the form. Once you have done so, you can save again. You may need to delete the file that was just saved before saving again, as overwriting is not currently allowed."
                    saveFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    self.userMessageBox.moveCursor(QTextCursor.End)

                if self.form.widget.state["accessDate"] == self.formDefaultState["accessDate"]:

                    messageText = "<br>WARNING: You indicated that this resource has an access level of \n'temporary-private\n' but did not provide a date at which the temporary-private access level would transition from private to either \n'public\n' or to \n'restricted-access\n'. Please return to the form to indicate the date at which temporary-provate access level will expire in the Access Date field on the form. Once you have done so, you can save again. You may need to delete the file that was just saved before saving again, as overwriting is not currently allowed."
                    saveFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    self.userMessageBox.moveCursor(QTextCursor.End)

            if self.editSingle:
                self.editSingle = False
                messageText = "<br><b>WARNING: Exiting edit mode.</b> If you need to continue editing this single resource file that is part of a larger multi \'like\' file resource, or if you need to edit another existing resource file, please close out of this form and start again by using the Edit Existing Resource button on the Add Resource Sub-tab of the Resource Tracker Tab. You can clear this form using the Clear Form button above the form to use this form to continue annotating new resource files."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))



            #saveFormat = '<span style="color:green;">{}</span>'
            #self.userMessageBox.append(saveFormat.format(messageText))
            #self.userMessageBox.setText(self.messageText)
            self.userMessageBox.moveCursor(QTextCursor.End)

    def clear_form(self):

        self.popFormField = []

        clearState = deepcopy(self.form.widget.state)
        #clearState = currentState.fromkeys(currentState, None)

        print(clearState) # form state before clear

        for key, value in clearState.items():
            print(key, value)
            if type(value) is str:
                clearState[key] = ""
            if type(value) is list:
                clearState[key] = []

        print(clearState) # form state totally cleared
        
        for key, value in clearState.items():
            print(key, value)
            if key in self.formDefaultState.keys():
                print("yes")
                clearState[key] = self.formDefaultState[key]
        
        print(clearState) # form state with default values added back in

        for key, value in self.form.widget.state.items():
            #self.form.widget.state[key] = clearState[key]

            self.form.widget.state = {
                key: clearState[key]
            } 

        #self.form.widget.state = deepcopy(clearState)
        print(self.form.widget.state)

        if self.lstbox_view.count() > 0:
            self.lstbox_view.clear()
            self.get_items_list()
        else:
            if self.items:
                self.items = []

        if self.lstbox_view2.count() > 0:
            self.lstbox_view2.clear()
            self.get_items_list2()
        else:
            if self.items2:
                self.items2 = []

        if self.editSingle:
            self.editSingle = False
            messageText = "<br><b>WARNING: Exiting edit mode.</b> If you need to continue editing this single resource file that is part of a larger multi \'like\' file resource, or if you need to edit another existing resource file, please close out of this form and start again by using the Edit Existing Resource button on the Add Resource Sub-tab of the Resource Tracker Tab. You can clear this form using the Clear Form button above the form to use this form to continue annotating new resource files."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

        messageText = "<br>Your form was successfully cleared and you can start annotating a new resource"
        saveFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(saveFormat.format(messageText))
        self.userMessageBox.moveCursor(QTextCursor.End)

        self.get_id()

        # messageText = "<br>NOTE: The Resource ID in your form has been re-set to the default value of \n'resource-1\n'. If you know which resource IDs you've already used, you can change the Resource ID in the cleared form manually by adding 1 to the max Resource ID you've already used. To generate a unique Resource ID automatically, click the Add DSC Package Directory button above the form - this will re-add your DSC Package Directory, search that directory for Resource IDs already used, generate a unique Resource ID by adding 1 to the max Resource ID already in use, and add that Resource ID value to the form for you."
        # saveFormat = '<span style="color:blue;">{}</span>'
        # self.userMessageBox.append(saveFormat.format(messageText)) 
        self.userMessageBox.moveCursor(QTextCursor.End)           

    def load_file(self):
        #_json_filter = 'json (*.json)'
        #f_name = QFileDialog.getOpenFileName(self, 'Load data', '', f'{_json_filter};;All (*)')
        print("in load_file fx")
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Resource Txt Data file you want to edit",
        #        (QtCore.QDir.homePath()), "Text (*.txt)")

        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Resource Txt Data file you want to edit",
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

            # if user selects a resource txt file that is not in the working data pkg dir, return w informative message
            if Path(self.saveFolderPath) != Path(ifileName).parent:
                messageText = "<br>You selected a resource txt file that is not in your working Data Package Directory; You must select a resource txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br> To proceed, close this form and return to the main DSC Data Packaging Tool window."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            self.saveFolderPath = Path(ifileName).parent
            print("saveFolderPath: ", self.saveFolderPath)
            
            with open(ifileName, 'r') as stream:
                data = load(stream)

            self.resource_id = data["resourceId"]
            self.resIdNum = int(self.resource_id.split("-")[1])
            self.resourceFileName = 'resource-trk-'+ self.resource_id + '.txt'
            #self.saveFilePath = os.path.join(self.saveFolderPath,self.resourceFileName)

            # make sure an archive folder exists, if not create it
            if not os.path.exists(os.path.join(self.saveFolderPath,"archive")):
                os.makedirs(os.path.join(self.saveFolderPath,"archive"))

            # move the resource annotation file user opened for editing to archive folder
            os.rename(ifileName,os.path.join(self.saveFolderPath,"archive",self.resourceFileName))
            messageText = "<br>Your original resource annotation file has been archived at:<br>" + os.path.join(self.saveFolderPath,"archive",self.resourceFileName) + "<br><br>"
            saveFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

            if data["associatedFileResultsDependOn"]:
                self.popFormField = data.pop("associatedFileResultsDependOn")
            
            self.form.widget.state = data

            if data["associatedFileMultiLikeFiles"]: 
                self.lstbox_view.addItems(data["associatedFileMultiLikeFiles"])
                self.add_multi_resource()
                self.take_inputs()

            if len(data["associatedFileDependsOn"]) > 2: 
                self.lstbox_view2.addItems(data["associatedFileDependsOn"])
                self.add_multi_depend()

    def take_inputs(self):

        editOptions =["Single file within multi \'like\' file resource", "All files within multi \'like\' file resource"]
        editOption, done = QtWidgets.QInputDialog.getItem(
          self, 'Edit Mode', 'You have selected a resource file that was originally annotated as part of a multi \'like\' file resource. Would you like to edit the annotation for just this one single resource file, or would you like to use this form to edit the annotation for all resource files that are part of the multi \'like\' file resource?', editOptions)

        if done:
            if str(editOption).startswith("Single"):
                self.editSingle = True
                messageText = "Edits you make in this form will be applied <b>only to this single resource file</b>. All other resource files within the larger multi \'like\' file resource of which this resource file is a part will remain unaltered."
                saveFormat = '<span style="color:blue;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
            else:
                messageText = "Edits you make in this form will be applied <b>to all resource files</b> within the larger multi \'like\' file resource of which this resource file is a part."
                saveFormat = '<span style="color:blue;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText)) 
                
                # if the user used the drag and drop to add multiple files, get a list of resource ids num, resource id, resource file name, and resource file save path for each file added
        
                self.resIdNumList = [self.resIdNum]
                self.resource_id_list = []
                self.resourceFileNameList = []
                self.saveFilePathList = []
        
                # assign a resource id to every resource file path added, construct a save file path for each resource
                if self.items:
                    print("self.items: ", self.items)
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
                        self.archiveFilePathList = [os.path.join(self.saveFolderPath,"archive",l) for l in self.resourceFileNameList]
                        print(self.saveFilePathList)

                        # already archived the first file so remove from list
                        self.saveFilePathList.pop(0)
                        self.archiveFilePathList.pop(0) # already archived the first file so remove from list

                        for p, archiveP in zip(self.saveFilePathList,self.archiveFilePathList):
                            # move the resource annotation file user opened for editing to archive folder
                            print(p, "; ", archiveP)
                            os.rename(p, archiveP)
                            messageText = "<br>Your original resource annotation file has been archived at:<br>" + archiveP + "<br>"
                            saveFormat = '<span style="color:blue;">{}</span>'
                            self.userMessageBox.append(saveFormat.format(messageText))





                  

        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateResourceWindow()
    window.show()
    sys.exit(app.exec_())