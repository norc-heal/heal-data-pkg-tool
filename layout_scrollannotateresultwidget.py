import sys
import os
from json import dumps, loads, load

from qtpy import QtWidgets

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

from schema_results_tracker import schema_results_tracker
from dsc_pkg_utils import qt_object_properties, get_multi_like_file_descriptions
import pandas as pd
import numpy as np
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

import json
import datetime
import jsonschema
from jsonschema import validate
from healdata_utils.validators.jsonschema import validate_against_jsonschema

class ScrollAnnotateResultWindow(QtWidgets.QMainWindow):
    def __init__(self, workingDataPkgDirDisplay, workingDataPkgDir, mode = "add"):
        super().__init__()
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.workingDataPkgDir = workingDataPkgDir
        self.mode = mode
        self.schemaVersion = schema_results_tracker["version"]
        self.loadingFormDataFromFile = False
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
        
        self.schema = schema_results_tracker
        
        self.experimentNameList = []
        #self.experimentNameList = self.get_exp_names() # gets self.experimentNameList
        self.experimentNameList, _ = dsc_pkg_utils.get_exp_names(self=self, perResource=False) # gets self.experimentNameList

        print("self.experimentNameList: ",self.experimentNameList)
        
        if self.experimentNameList:
            #self.schema = self.add_exp_names_to_schema() # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList
            self.schema = dsc_pkg_utils.add_exp_names_to_schema(self=self) # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList

        self.ui_schema = {}
        
        self.builder = WidgetBuilder(self.schema)
        self.form = self.builder.create_form(self.ui_schema)
        
        self.formDefaultState = {
            "schemaVersion": self.schemaVersion,
            "resultId": "result-1",
            "experimentNameBelongsTo": "default-experiment-name"
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
        self.buttonSaveResult = QtWidgets.QPushButton(text="Save result",parent=self)
        self.buttonSaveResult.clicked.connect(self.save_result)

        self.buttonSaveResult.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonSaveResult.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
        

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
   
        # create button to add multiple file dependencies addition
        self.buttonAddMultiDepend = QtWidgets.QPushButton(text="Add Multiple Result Dependencies",parent=self)
        self.buttonAddMultiDepend.clicked.connect(self.add_multi_depend)
        self.labelAddMultiDepend = QtWidgets.QLabel(text="To add multiple file dependencies for your result, <b>drag and drop file paths right here</b>. If your result has one or just a few dependencies, you can drag and drop them here or browse to each dependency (one dependency at a time) using the Associated Files/Dependencies field in the form below.",parent=self)
        
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

        # check for emptyp tooltip content whenever form changes and replace empty tooltip with original tooltip content
        # (only relevant for fields with in situ validation - i.e. string must conform to a pattern - as pyqtschema will replace the 
        # tooltip content with some error content, then replace the content with empty string once the error is cleared - this check will
        # restore the original tooltip content - for efficiency, may want to only run this when a widget that can have validation 
        # errors changes - #TODO)
        self.form.widget.on_changed.connect(self.check_tooltip)
        self.formWidgetList[self.formWidgetNameList.index("category")].on_changed.connect(self.conditional_fields)
        
        
        ################################## Finished creating component widgets
        

        #self.vbox.addWidget(self.buttonAddDir)
        self.vbox.addWidget(self.buttonSaveResult)
        self.vbox.addWidget(self.buttonClearForm)
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
        
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
        self.setWindowTitle("Annotate Result")
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

    # def get_exp_names(self):
        
    #     getDir = self.workingDataPkgDir
    #     getExpTrk = os.path.join(getDir,"heal-csv-experiment-tracker.csv")

    #     if os.path.isfile(getExpTrk):
    #         experimentTrackerDf = pd.read_csv(getExpTrk)
    #         #experimentTrackerDf.replace(np.nan, "")
    #         experimentTrackerDf.fillna("", inplace = True)

    #         print(experimentTrackerDf)
    #         print(experimentTrackerDf.columns)

    #         if "experimentName" in experimentTrackerDf.columns:
    #             experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
    #             print(experimentTrackerDf["experimentName"])                
    #             experimentNameList = experimentTrackerDf["experimentName"].unique().tolist()
    #             print(experimentNameList,type(experimentNameList))
    #             experimentNameList[:] = [x for x in experimentNameList if x] # get rid of emtpy strings as empty strings are not wanted and mess up the sort() function
    #             print(experimentNameList,type(experimentNameList))

    #             #sortedlist = sorted(list, lambda x: x.rsplit('-', 1)[-1])
    #             experimentNameList = sorted(experimentNameList, key = lambda x: x.split('-', 1)[0])

    #             #experimentName = sorted(experimentNameList, lamda x: x.split('-'))
    #             print(experimentNameList,type(experimentNameList))

    #             # if ((len(experimentNameList) == 1) and (experimentNameList[0] == "default-experiment-name")):
    #             #     experimentNameList = []
    #             #experimentNameList.remove("default-experiment-name")
    #             #print(experimentNameList,type(experimentNameList))
    #         else:
    #             print("no experimentName column in experiment tracker")
    #             experimentNameList = []
    #     else:
    #         print("no experiment tracker in working data pkg dir")
    #         # messageText = "<br>Your working Data Package Directory does not contain a properly formatted Experiment Tracker from which to populate unique experiment names for experiments you've already documented. <br><br> The field in this form <b>Experiment Result \"Belongs\" To</b> pulls from this list of experiment names to provide options of study experiments to which you can link your results. Because we cannot populate this list without your experiment tracker, your only option for this field will be the default experiment name: \"default-experiment-name\"." 
    #         # errorFormat = '<span style="color:red;">{}</span>'
    #         # self.userMessageBox.append(errorFormat.format(messageText)) 
    #         experimentNameList = []

    #     print("experimentNameList: ", experimentNameList)
    #     return experimentNameList
            
    # def add_exp_names_to_schema(self):

    #     schemaOrig = self.schema
    #     experimentNameList = self.experimentNameList

    #     experimentNameListUpdate = {}
        
    #     schemaUpdated = deepcopy(schemaOrig)
    #     enumListOrig = schemaUpdated["properties"]["experimentNameBelongsTo"]["enum"]
    #     print("enumListOrig: ", enumListOrig)
    #     #enumListUpdated = enumListOrig.extend(experimentNameList)
    #     enumListUpdated = experimentNameList
    #     print("enumListUpdated: ", enumListUpdated)

    #     schemaUpdated["properties"]["experimentNameBelongsTo"]["enum"] = enumListUpdated
    #     print("schemaOrig: ",schemaOrig)
    #     print("schemaUpdated: ", schemaUpdated)

    #     return schemaUpdated

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

        # this is an inefficient way to make sure previously unhidden fields get hidden again if user changes the category
        # should really save the last chosen state and be selective about re-hiding the ones that were revealed due to the
        # previous selection

        ################### hide fields that were revealed due to previous selection

        if self.form.widget.state["category"] not in ["single-panel-figure","figure-panel"]:
            self.toggle_widgets(keyText = "figure", desiredToggleState = "hide")
            # delete contents of conditional fields if any added

            # DO NOT do these items if loading from file (i.e. user is editing an existing annotation or adding a new annotation based on existing) 
            if not self.loadingFormDataFromFile:
                self.form.widget.state = {
                    "figureNumber": []
                }

        if self.form.widget.state["category"] != "table":
            self.toggle_widgets(keyText = "table", desiredToggleState = "hide")
            # delete contents of conditional fields if any added
            
            # DO NOT do these items if loading from file (i.e. user is editing an existing annotation or adding a new annotation based on existing) 
            if not self.loadingFormDataFromFile:
                self.form.widget.state = {
                    "tableNumber": []
                }  
            
        ################### show field appropriate to current selection
            
        if self.form.widget.state["category"] in ["single-panel-figure","figure-panel"]:
            self.toggle_widgets(keyText = "figure", desiredToggleState = "show")

        if self.form.widget.state["category"] == "table":
            self.toggle_widgets(keyText = "table", desiredToggleState = "show")
          
    def add_dir(self):
        
        #self.saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new result will be saved there!')
        self.saveFolderPath = self.workingDataPkgDir

    def get_id(self):

        if self.saveFolderPath:

            # get new result ID for new result file - get the max id num used for existing result files and add 1; if no result files yet, set id num to 1
        
            resFileList = [filename for filename in os.listdir(self.saveFolderPath) if filename.startswith("result-trk-result-")]
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

            self.form.widget.state = {
                    "resultIdNumber": self.resIdNum
                }

            self.result_id = 'result-'+ str(self.resIdNum)
            self.resultFileName = 'result-trk-'+ self.result_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

            messageText = "<br>Based on other results already saved in your working DSC Data Package directory, your new result will be saved with the unique ID: " + self.result_id + "<br>Result ID has been added to the result form."
            messageText = messageText + "<br><br>Your new result file will be saved in your working DSC Data Package directory as: " + self.saveFilePath + "<br><br>"
            self.userMessageBox.append(messageText)
            #self.userMessageBox.moveCursor(QTextCursor.End)

            # # if there's not a results tracker template already in the directory they added
            # # let them proceed but provide an informative warning
            # dscDirFilesList = [f for f in os.listdir(self.saveFolderPath) if os.path.isfile(f)]
            # dscDirFilesStemList = [Path(f).stem for f in dscDirFilesList]
            # if not any(x.startswith("heal-csv-results-tracker") for x in dscDirFilesStemList):
            #     messageText = "<br>Warning: It looks like there is no HEAL formatted result tracker in the directory you selected. Are you sure you selected a directory that is a DSC package directory and that you have created a HEAL formatted result tracker? If you have not already created a DSC package directory, you can do so now by navigating to the DSC Package tab in the application, and clicking on the Create sub-tab. This will create a directory called \n'dsc-pkg\n' which will have a HEAL formatted resource tracker and experiment tracker file inside. You can create a HEAL formatted result tracker (please create one per multi-result file - e.g. poster, publication, etc. - you will share) by navigating to the Result Tracker tab, and the Create Result Tracker sub-tab. You may save your result-tracker in your DSC Package directory, but this is not required. Once you've created your DSC Package Directory and created a HEAL formatted Result Tracker, please return here and add your DSC package directory before proceeding to annotate your result(s). While annotating your result(s) you will also need to add the HEAL formatted result tracker you created."
            #     errorFormat = '<span style="color:red;">{}</span>'
            #     self.userMessageBox.append(errorFormat.format(messageText))

            self.form.widget.state = {
                "resultId": self.result_id
            }

        # this should no longer be necessary as the form widget will only be opened if a workingDataPkgDir has been set and the path has been as a string 
        else:
            messageText = "<br>Please select your DSC Package Directory to proceed."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        
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
                
    def add_multi_depend(self):

        if ((self.lstbox_view2.isHidden()) and (self.labelAddMultiDepend.isHidden())):
            self.lstbox_view2.show()
            self.labelAddMultiDepend.show()
        else:
            self.lstbox_view2.hide()
            self.labelAddMultiDepend.hide()

    def save_result(self):

        result = deepcopy(self.form.widget.state)
        #dumps(result, indent=4)

        # for any array of string items, remove empty strings from array
        for key in self.schema["properties"]:
            if self.schema["properties"][key]["type"] == "array":
                if self.schema["properties"][key]["items"]["type"] == "string":
                    result[key] = dsc_pkg_utils.deleteEmptyStringInArrayOfStrings(myStringArray=result[key])

        if not dsc_pkg_utils.validateFormData(self=self,formData=result):
            return
        
        # this should no longer be necessary as the form will only be opened if a valid working data pkg dir has been set by the user and the path has been passed as a string to the form widget
        # check that a dsc data package dir has been added - this is the save folder
        if not self.saveFolderPath:
            messageText = "<br>You must add a DSC Data Package Directory before saving your result file. Please add a DSC Data Package Directory and then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # # check that file path for at least one associated publication and at least a minimal description has been added to the form 
        # # if not exit with informative error
        # if not ((self.form.widget.state["associatedFilePublication"]) and (self.form.widget.state["description"])):
        #     messageText = "<br>You must add at least a minimal description of your result and at least one associated publication file in which this result is shared/cited to your result annotation form before saving your result annotation form. Please add at least a minimal description of your result in the Result Description field in the form, and add at least one publication file in which this result appears by browsing to a file path(s) in the Associated Publication File(s) field in the form. Then try saving again." 
        #     errorFormat = '<span style="color:red;">{}</span>'
        #     self.userMessageBox.append(errorFormat.format(messageText))
        #     return

        # remove requirement for providing at least one associated publication at time of starting a result annotation
        # the idea here is that this allows flex for investigators to start annotating results as soon as they create a 
        # figure/table/etc that is likely to make it into a manuscript but drafting of manuscript has not yet started
        # if a user annotates a result prior to having a publication in which it is shared, they should leave the 
        # associated publication field blank but then come back and edit the result annotation/add this result annotation 
        # to the results tracker for the publication once they have started the publication or added this result definitively 
        # to an existing publication - 
        # now only check that at least a minimal description has been added to the form 
        # if not exit with informative error
        #if not self.form.widget.state["description"]:
        if not result["description"]:
            messageText = "<br>You must add at least a minimal description of your result before saving your result annotation form. Please add at least a minimal description of your result in the Result Description field in the form. Then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # if the user didn't add an associated publication, provide a little warning/informative message
        # indicating that if they already know the associated pub they should add it right away by editing the result annotation
        # and if they don't already know it that they should edit once they do in order to ensure the result is 
        # appropriately added to the publication's results tracker
        # importantly, this does not stop the user from saving the result annotation
        #if not self.form.widget.state["associatedFilePublication"]:
        if not result["associatedFilePublication"]:
            messageText = "<br><b>WARNING:</b> You did not indicate an associated publication file in which this result is or will be shared. If you already know which publication(s) this result will be shared in, please return to the \"Add Result\" tab and use the \"Edit an existing result\" push-button to edit this result annotation and add the publication(s) in which the result will be shared. You can add at least one publication file in which this result is/will be shared by browsing to a file path(s) in the Associated Publication File(s) field in the form. <br><br>If, at this time, you have not started drafting the publication in which this result will be shared, or don't know yet in which publication this result will be shared, please return to edit the result annotation once you have started drafting the publication or decided in which publication this result will be shared. Doing so will ensure that this result is added to the Results Tracker for the publication(s) in which it is shared!" 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            #return
        
        if self.mode == "edit":
            # move the annotation file user opened for editing to archive folder
            #os.rename(ifileName,os.path.join(self.saveFolderPath,"archive",self.annotationArchiveFileName))
            os.rename(self.saveFilePath,self.saveAnnotationFilePath)
            messageText = "<br>In preparation for saving your edited result annotation file, your original result annotation file has been archived at:<br>" + self.saveAnnotationFilePath + "<br><br>"
            saveFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

        # check if user has modified the result id from the one that was autogenerated when adding dsc data dir for saving
        # this may happen if for example a user annotates a result using the autogenerated id, then wants to keep 
        # going using the same form window instance, modify the contents to annotate a new result (perhaps one with some 
        # form fields that will be the same), and save again with a new id - in this case the user can modify the 
        # id manually, incrementing the id number by one - if id modified, updated it in memory and regenerate
        # the save file name, save file path, and id number
        #if self.form.widget.state["resultId"] != self.result_id:
        if result["resultId"] != self.result_id:
            
            #self.result_id = self.form.widget.state["resultId"]
            self.result_id = result["resultId"]
            self.resultFileName = 'result-trk-'+ self.result_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

            self.resIdNum = int(self.result_id.split("-")[1])
        
        # check if saveFilePath already exists (same as if a file for this resource id already exists); if exists, exit our with informative message;
        # otherwise go ahead and save
        if os.path.isfile(self.saveFilePath):
            messageText = "A result annotation for a result with id " + self.result_id + " already exists at " + self.saveFilePath + "<br><br>You may want to do one or both of: 1) Use the View/Edit tab to view your result tracker file(s) and check which result IDs you've already used and added to your tracker(s), 2) Use File Explorer to navigate to your DSC Data Package Directory and check which result IDs you've already used and for which you've already created result files - these files will be called \'result-trk-result-{a number}.txt\'. While you perform these checks, your result tracker form will remain open unless you explicitly close it. You can come back to it, change your result ID, and hit the save button again to save with a result ID that is not already in use. If you meant to edit an existing result annotation file, please use the \"Edit an existing result\" functionality on the \"Add a result\" sub-tab.<br><br>" 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        else:
                              
            #result = self.form.widget.state
            f=open(self.saveFilePath,'w')
            print(dumps(result, indent=4), file=f)
            f.close()
                
            #self.messageText = self.messageText + '\n\n' + "Your resource file was successfully written at: " + self.saveFilePath + '\n' + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
            messageText = "<br>Your result was successfully written at: " + self.saveFilePath + "<br><br> Starting to add your result to Results Tracker now! See below for updates: <br>" 
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            self.userMessageBox.moveCursor(QTextCursor.End)

            QApplication.processEvents() # print accumulated user status messages 

            self.auto_add_result() # add experiment file to experiment tracker

    def auto_add_result(self):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # experiment tracker is needed to populate the enum of experimentNameBelongsTo schema property (in this case for validation purposes) so perform some checks

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br> The result was saved but was not added to a Results Tracker. To add this result to a Results Tracker, first set your working Data Package Directory, then navigate to the \"Results Tracker\" tab >> \"Add Result\" sub-tab and click on the \"Batch add result(s) to tracker\" push-button. You can select just this result, or all results to add to Results Tracker. If some results you select to add to Results Tracker have already been added they will be not be re-added."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
                messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br><br>The result was saved but was not added to a Results Tracker. To add this result to a Results Tracker, first set your working Data Package Directory, then navigate to the \"Results Tracker\" tab >> \"Add Result\" sub-tab and click on the \"Batch add result(s) to tracker\" push-button. You can select just this result, or all results to add to Results Tracker. If some results you select to add to Results Tracker have already been added they will be not be re-added"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

        # don't check for results tracker exists as this function checks for appropriate trackers already existing and creates the needed results tracker(s) if they don't already exist
        # # check that resource tracker exists in working data pkg dir, if not, return
        # if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-resource-tracker.csv")):
        #     messageText = "<br>There is no Resource Tracker file in your working Data Package Directory; Your working Data Package Directory must contain a Resource Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br>"
        #     saveFormat = '<span style="color:red;">{}</span>'
        #     self.userMessageBox.append(saveFormat.format(messageText))
        #     return
        
        # check that all results trackers are closed (user doesn't have it open in excel for example)
        resultsTrackersList = [filename for filename in os.listdir(self.workingDataPkgDir) if filename.startswith("heal-csv-results-tracker-")]
        print("results trackers: ", resultsTrackersList)
        
        if resultsTrackersList:
            for tracker in resultsTrackersList:

                try: 
                    with open(os.path.join(self.workingDataPkgDir,tracker),'r+') as f:
                        print("file is closed, proceed!!")
                except PermissionError:
                        messageText = "<br>At least one Results Tracker file that already exists in your working Data Package Directory is open in another application, and must be closed to proceed; Check if any Results Tracker files are open in Excel or similar application, and close the file(s). <br><br>The result was saved but was not added to a Results Tracker. To add this result to a Results Tracker, first set your working Data Package Directory, then navigate to the \"Results Tracker\" tab >> \"Add Result\" sub-tab and click on the \"Batch add result(s) to tracker\" push-button. You can select just this result, or all results to add to Results Tracker. If some results you select to add to Results Tracker have already been added they will be not be re-added."
                        saveFormat = '<span style="color:red;">{}</span>'
                        self.userMessageBox.append(saveFormat.format(messageText))
                        return

        # get result file path
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Result Txt Data file(s)",
        #        (QtCore.QDir.homePath()), "Text (*.txt)")

        # open files select file browse to working data package directory
        # ifileName, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select the Input Result Txt Data file(s) from your working Data Package Directory",
        #        self.workingDataPkgDir, "Text (*.txt)")
        ifileName = [self.saveFilePath]
        
        if ifileName:

            
            # check that all files are result annotation files, if not, return
            fileStemList = [Path(filename).stem for filename in ifileName]
            print(fileStemList)
            checkFileStemList = [stem.startswith("result-trk-result-") for stem in fileStemList]
            print(checkFileStemList)
            
            if not all(checkFileStemList):
                messageText = "<br>The files you selected may not all be result txt files. Result txt files must start with the prefix \"result-trk-result-\". <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            # just for the first annotation file selected for addition to the tracker, check to make sure it is 
            # in the working data pkg dir - if not return with informative message
            ifileNameCheckDir = ifileName[0]

            # if user selects a result txt file that is not in the working data pkg dir, return w informative message
            if Path(self.workingDataPkgDir) != Path(ifileNameCheckDir).parent:
                messageText = "<br>You selected a result txt file that is not in your working Data Package Directory; You must select a result txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #countFiles = len(ifileName)

            # initialize lists to collect valid and invalid files
            validFiles = []
            invalidFiles = []

            # don't need to do this in this context as schema has already been dynamically updated (don't need a lot of the above checks either - should clean the auto add function in this widget up..)
            # # dynamically update schema
            # self.schema = schema_results_tracker

            # self.experimentNameList = []
            # self.experimentNameList = dsc_pkg_utils.get_exp_names(self=self) # gets self.experimentNameList
            # print("self.experimentNameList: ",self.experimentNameList)
            # if self.experimentNameList:
            #     #self.schema = self.add_exp_names_to_schema() # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList
            #     self.schema = dsc_pkg_utils.add_exp_names_to_schema(self=self) # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList

            
            # initialize an empty dataframe to collect data from each file in ifileName
            # one row will be added to collect_df for each valid file in ifileName
            collect_df = pd.DataFrame([])
            
            for filename in ifileName:
                print(filename)

                
                
                # get result id and filename stem
                ifileNameStem = Path(filename).stem
                IdNumStr = ifileNameStem.rsplit('-',1)[1]
                result_id = "result-" + IdNumStr
                print("result-id: ", result_id)
                
                # load data from result file and convert to python object
                #path = ifileName
                path = filename
                data = json.loads(Path(path).read_text())
                print(data)

                # validate experiment file json content against experiment tracker json schema
                #out = validate_against_jsonschema(data, schema_results_tracker)
                out = validate_against_jsonschema(data, self.schema)
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
                    messageText = "The following result file is NOT valid and will not be added to a Results Tracker file: " + filename + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + printErrAll + "\n\n\n"
                    
                    self.userMessageBox.append(messageText)
                    #return
                    # switch from return to break so that if user selects more than one file, and one is not valid, can skip to next file and continue instead of returning fully out of the function
                    #break
                    continue 

                # if valid, continue:
                else:
                    #messageText = "The following resource file is valid: " + ifileName
                    messageText = "The following result file is valid: " + filename
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
                    #                 "resultIdNumber": [int(IdNumStr)],  
                    #                 #"annotationCreateDateTime": [restrk_c_datetime],
                    #                 #"annotationModDateTime": [restrk_m_datetime],
                    #                 "annotationModTimeStamp": [restrk_m_timestamp]}


                    # add_to_df = pd.DataFrame(add_to_df_dict)

                    # convert json to pd df
                    df = pd.json_normalize(data) # df is a one row dataframe
                    print(df)
                    df["annotationCreateDateTime"][0] = restrk_c_datetime
                    df["annotationModDateTime"][0] = restrk_m_datetime
                    df["resultIdNumber"][0] = int(IdNumStr)
                    df["annotationModTimeStamp"] = restrk_m_timestamp
                    print(df)
                    # df = pd.concat([df,add_to_df], axis = 1) # concatenate cols to df; still a one row dataframe
                    # print(df)

                    collect_df = pd.concat([collect_df,df], axis=0) # add this files data to the dataframe that will collect data across all valid data files
                    print("collect_df rows: ", collect_df.shape[0])

                    
        else: 
            print("you have not selected any files; returning")
            messageText = "<br>You have not selected any result files to add to the results tracker. Please select at least one result file to add."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # once you've looped through all selected files, if none are valid, print an informative message for the user listing
        # which files did not pass validation and exit
        if not validFiles:
            messageText = "The contents of the Result file(s): " + "\n\n\n" + ', '.join(invalidFiles) + "\n\n\n" + "cannot be added to a Results Tracker file because they did not pass validation. Please review the validation errors for the file(s) printed above." + "Exiting \"Add Result\" function now." 
            self.userMessageBox.append(messageText)
            return

        
        
        # you should now have collected one row of data from each valid data file and collected it into collect_df dataframe
        # now get location of dsc pkg dir, check if appropriate results trackers already exist, if not create them, then add
        # results to appropriate results trackers

        # no longer need to ask user to browse to dsc data package dir - instead use working data package dir set by user in data package tab of tool
        #dscDirPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your result(s) will be auto-added to appropriate Results Tracker(s) there!')
        dscDirPath = self.workingDataPkgDir

        if not dscDirPath:
            messageText = "You have not selected a directory. Please select your DSC Data Package Directory. If you have not yet created a DSC Data Package Directory, use the \"Create New Data Package\" button on the \"Create\" sub-tab of the \"Data Package\" tab to create a DSC Data Package Directory. You can then come back here and try adding your result file(s) again! <br><br>Exiting \"Add Result\" function now."
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return
        else:

            # # get the results with no assoc pub
            # collect_df_no_assoc_pub = collect_df[collect_df["associatedFilePublication"].isnull()]
            
            # # drop the results with no assoc pub from collect_df
            # collect_df = collect_df[~collect_df["associatedFilePublication"].isnull()]

            # if assoc pub is empty replace with an empty list - i don't think this is necessary so commenting out for now
            #d.loc[d['x'].isnull(),['x']] = d.loc[d['x'].isnull(),'x'].apply(lambda x: [])
            #collect_df.loc[collect_df["associatedFilePublication"].isnull(),["associatedFilePublication"]] = collect_df.loc[collect_df["associatedFilePublication"].isnull(),"associatedFilePublication"].apply(lambda x: [])
            

            # add dummies for whether or not each result is associated with any of the unique publication files listed in any of the result annotations
            # this will allow filtering to the df that should be written to each result tracker file (each result tracker file is named after a specific unique publication file)
            # if a result tracker does not yet exist in the dsc pkg dir for each unique publication file listed across all result files, this fx will create the appropriate results tracker file
            collect_df_cols = list(collect_df.columns)
            print("collect_df_cols: ", collect_df_cols)

            # check if none of the resulst have an associated pub - if none have an associated pub, set explode to False
            explode = True
            # if user didn't add a publication path but did click the button on the form to add a field in which to add a path, an empty string is saved to the array of file paths, get rid of those here
            collect_df["associatedFilePublication"] = [dsc_pkg_utils.deleteEmptyStringInArrayOfStrings(myStringArray = l) for l in collect_df["associatedFilePublication"]]
            
            if collect_df["associatedFilePublication"][0] == []:
                if collect_df.shape[0] == 1:
                    explode = False
                elif collect_df.shape[0] > 1:
                    check = all([True if v==[] else False for v in collect_df["associatedFilePublication"]])
                    if check:
                        explode = False

            # if at least one result has at least one associated pub create dummies for associated pub and add them to the collect df
            if explode: 
                myDummies = collect_df["associatedFilePublication"].str.join('|').str.get_dummies()
                print(list(myDummies.columns))
                collect_df = pd.concat([collect_df, myDummies], axis = 1)
            
            # add dummy var collect-all equal to 1 for all result entries; all results should be written to the collect-all results tracker
            collect_df["collect-all"] = 1

            # get a list of any results trackers that already exist in dsc pkg dir
            resultsTrkFileList = [filename for filename in os.listdir(dscDirPath) if filename.startswith("heal-csv-results-tracker")]
            print(resultsTrkFileList)
            resultsTrkFileList = [os.path.join(dscDirPath,filename) for filename in resultsTrkFileList]

            #if resultsTrkFileList: # if the list is not empty
            #    resultsTrkFileStemList = [Path(filename).stem for filename in resultsTrkFileList]
            #    print(resultsTrkFileStemList)
            #    
            #else:
            #    resultsTrkFileStemList = []

            # if at least one result has at least one assoc pub get the list of unique assoc pubs and 
            # unique results tracker file names needed to accomodate these results, then add the collect all results tracker
            # if none of the results have any assoc pub, just add the collect all results tracker to the list of 
            # unique results tracker file names needed to accomodate these results
            if explode: 
                publicationFileList = collect_df["associatedFilePublication"].explode().unique().tolist()
                print("publication file list: ",publicationFileList)
                publicationFileStemList = [Path(filename).stem for filename in publicationFileList]
                print(publicationFileStemList)
                finalResultsTrkFileStemList = ["heal-csv-results-tracker-"+ filename + ".csv" for filename in publicationFileStemList]
                # add the collect-all results tracker to the final results tracker list
                finalResultsTrkFileStemList = finalResultsTrkFileStemList + ["heal-csv-results-tracker-collect-all.csv"]
            else:
                finalResultsTrkFileStemList = ["heal-csv-results-tracker-collect-all.csv"]
            
            finalResultsTrkFileList = [os.path.join(dscDirPath,filename) for filename in finalResultsTrkFileStemList]
            print("result tracker file list: ", resultsTrkFileList)
            print("final result tracker file list: ", finalResultsTrkFileList)

            if resultsTrkFileList:
                trkExist = [filename for filename in finalResultsTrkFileList if filename in resultsTrkFileList]
                print(trkExist)
                #trkExist = [os.path.join(dscDirPath,filename) for filename in trkExist]
                #print(trkExist)

                for t in trkExist:
                    messageText = "Required results tracker already exists - new added results will be appended: <br>" + t
                    #errorFormat = '<span style="color:red;">{}</span>'
                    #self.userMessageBox.append(errorFormat.format(messageText))
                    self.userMessageBox.append(messageText)
            else: 
                trkExist = []


            trkCreate = [filename for filename in finalResultsTrkFileList if filename not in resultsTrkFileList]
            print(trkCreate)
            #trkCreate = [os.path.join(dscDirPath,filename) for filename in trkCreate]
            #print(trkCreate)

            if trkCreate:
                df, _ = dsc_pkg_utils.new_results_trk()

                for t in trkCreate:
                    df.to_csv(t, index = False) 
                    messageText = "A new results tracker has been created - added results will be the first content: <br>" + t
                    #errorFormat = '<span style="color:red;">{}</span>'
                    #self.userMessageBox.append(errorFormat.format(messageText))
                    self.userMessageBox.append(messageText)

            else: 
                trkCreate = []

            if explode:
                publicationFileList = publicationFileList + ["collect-all"]
            else:
                publicationFileList = ["collect-all"] 

            print("publicationFileList: ", publicationFileList)
            print("finalResultsTrkFileList: ",finalResultsTrkFileList)
            
            for m, t in zip(publicationFileList, finalResultsTrkFileList):
                print(m,"; ",t)
                print_df = collect_df[collect_df[m] == 1]
                print(print_df.shape)
                print(print_df.columns)
                print_df = print_df[collect_df_cols]
                print(print_df.shape)
                print(print_df.columns)

                writeResultsList = print_df["resultId"].tolist()
                writeResultsFileList = ["result-trk-" + r for r in writeResultsList]
                
                output_path = t
                all_df = pd.read_csv(output_path)
                #all_df = pd.concat([all_df, df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
                all_df = pd.concat([all_df, print_df], axis=0) # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
            
                all_df.sort_values(by = ["resultIdNumber"], inplace=True)
                # drop any exact duplicate rows
                #all_df.drop_duplicates(inplace=True) # drop_duplicates does not work when df includes list vars
                # this current approach does not appear to be working at the moment
                print("all_df rows, with dupes: ", all_df.shape[0])
                all_df = all_df[-(all_df.astype('string').duplicated())]
                print("all_df rows, without dupes: ", all_df.shape[0])
            
                # before writing to file may want to check for duplicate result IDs and if duplicate result IDs, ensure that 
                # user wants to overwrite the earlier instance of the result ID in the results tracker - right now, dup entries 
                # for a result are all kept as long as not exact dup (i.e. at least one thing has changed)

                all_df.to_csv(output_path, mode='w', header=True, index=False)
                #df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

                messageText = "The contents of the Result file(s): <br><br>" + ', '.join(writeResultsFileList) + "<br><br>were added as a result(s) to the Results Tracker file: <br><br>" + output_path + "<br><br>"
                errorFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))

            if invalidFiles:
                messageText = "The contents of the Result file(s): <br><br>" + ', '.join(invalidFiles) + "<br><br>cannot be added to a Results Tracker file because they did not pass validation. Please review the validation errors printed above." 
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
            
    
    def clear_form(self):

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

        if self.lstbox_view2.count() > 0:
            self.lstbox_view2.clear()
            self.get_items_list2()
        else:
            if self.items2:
                self.items2 = []

        
        messageText = "<br>Your form was successfully cleared and you can start annotating a new result"
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

        self.loadingFormDataFromFile = True

        if self.mode == "edit":
            textBit = "edit"
            textButton = "\"Edit an existing result\""
        elif self.mode == "add-based-on":
            textBit = "base a new result upon"
            textButton = "\"Add a new result based on an existing result\""

        
        ifileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the Result txt file you want to " + textBit,
            self.saveFolderPath, "Text (*.txt)")

        if not ifileName: 
            messageText = "<br>You have not selected a file to " + textBit + ". Close this form now. If you still want to " + textBit + " an existing result, Navigate to the \"Result Tracker\" tab >> \"Add Result\" sub-tab and click the " + textButton + " push-button."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText)) 
        else: 
            #self.editMode = True
                     
            #self.saveFilePath = ifileName
            print("saveFilePath: ", self.saveFilePath)
            print(Path(ifileName).parent)
            print(Path(self.saveFolderPath))

            # add check on if filename starts with result-trk-result?
            if not Path(ifileName).stem.startswith("result-trk-result-"):
                messageText = "<br>The file you selected may not be a result txt file - a result txt file will have a name that starts with \"result-trk-result-\" followed by a number which is that result's ID number. You must select a result txt file that is in your working Data Package Directory to proceed. <br><br> To proceed, close this form and return to the main DSC Data Packaging Tool window."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            # add check on if valid result-trk file?

            # if user selects a result txt file that is not in the working data pkg dir, return w informative message
            if Path(self.saveFolderPath) != Path(ifileName).parent:
                messageText = "<br>You selected a result txt file that is not in your working Data Package Directory; You must select a result txt file that is in your working Data Package Directory to proceed. If you need to change your working Data Package Directory, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory. <br><br> To proceed, close this form and return to the main DSC Data Packaging Tool window."
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            #self.saveFolderPath = Path(ifileName).parent
            print("saveFolderPath: ", self.saveFolderPath)
            
            with open(ifileName, 'r') as stream:
                data = load(stream)

            if self.mode == "add-based-on":
                based_on_annotation_id = data["resultId"]

            if self.mode == "edit": 
                self.result_id = data["resultId"]
                self.resIdNum = int(self.result_id.split("-")[1])

                self.resultFileName = 'result-trk-'+ self.result_id + '.txt'
                
                # save the full path at which the current file is saved and at which you will save the newly edited file if possible (e.g. valid, tool does not crash for any reason)
                self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

                # # make sure an archive folder exists, if not create it
                # if not os.path.exists(os.path.join(self.saveFolderPath,"archive")):
                #     os.makedirs(os.path.join(self.saveFolderPath,"archive"))

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

                # save full path at which you will archive the file once the new file is saved
                self.saveAnnotationFilePath = os.path.join(self.saveFolderPath,"archive",self.annotationArchiveFileName)

                # move this to end of save command and only do it if in edit mode
                # # move the result annotation file user opened for editing to archive folder
                # #os.rename(ifileName,os.path.join(self.saveFolderPath,"archive",self.annotationArchiveFileName))
                # os.rename(ifileName,self.saveAnnotationFilePath)
                # messageText = "<br>Your original result annotation file has been archived at:<br>" + self.saveAnnotationFilePath + "<br><br>"
                # saveFormat = '<span style="color:blue;">{}</span>'
                # self.userMessageBox.append(saveFormat.format(messageText))

            self.form.widget.state = data

            if len(data["associatedFileDependsOn"]) > 2: 
                self.lstbox_view2.addItems(data["associatedFileDependsOn"])
                self.add_multi_depend()   

            if self.mode == "edit":
                self.form.widget.state = {
                    "resultIdNumber": self.resIdNum
                }

            if self.mode == "add-based-on":
                self.get_id()
                messageText = "<br>Your new result has been initialized based on information you entered for " + based_on_annotation_id + "<br><br>"
                saveFormat = '<span style="color:blue;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))      

        self.loadingFormDataFromFile = False
        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateResultWindow()
    window.show()
    sys.exit(app.exec_())