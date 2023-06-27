import sys
import os
from json import dumps, loads

from qtpy import QtWidgets

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

from schema_results_tracker import schema_results_tracker
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

class ScrollAnnotateResultWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.ui_schema = {}
        
        self.builder = WidgetBuilder(self.schema)
        self.form = self.builder.create_form(self.ui_schema)
        
        self.formDefaultState = {
            "result.id": "result-1"
        }

        self.form.widget.state = deepcopy(self.formDefaultState)
      
         # create 'add dsc data pkg directory' button
        self.buttonAddDir = QtWidgets.QPushButton(text="Add DSC Package Directory",parent=self)
        self.buttonAddDir.clicked.connect(self.add_dir)

        self.buttonAddDir.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonAddDir.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
                

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
        

        self.vbox.addWidget(self.buttonAddDir)
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

        if self.form.widget.state["category"] != "figure":
            self.toggle_widgets(keyText = "figure", desiredToggleState = "hide")
            # delete contents of conditional fields if any added
            self.form.widget.state = {
                "figure.number": []
            } 
            
        ################### show field appropriate to current selection
            
        if self.form.widget.state["category"] == "figure":
            self.toggle_widgets(keyText = "figure", desiredToggleState = "show")
          
    def add_dir(self):
        
        self.saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new result will be saved there!')
        
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
            self.result_id = 'result-'+ str(self.resIdNum)
            self.resultFileName = 'result-trk-'+ self.result_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

            messageText = "<br>Based on other results already saved in your DSC Package directory, your new result will be saved with the unique ID: " + self.result_id + "<br>Result ID has been added to the result form."
            messageText = messageText + "<br>Your new result file will be saved in your DSC Package directory as: " + self.saveFilePath + "<br><br>"
            self.userMessageBox.append(messageText)
            #self.userMessageBox.moveCursor(QTextCursor.End)

            # if there's not a resource tracker template already in the directory they added
            # let them proceed but provide an informative warning
            dscDirFilesList = [f for f in os.listdir(self.saveFolderPath) if os.path.isfile(f)]
            dscDirFilesStemList = [Path(f).stem for f in dscDirFilesList]
            if not any(x.startswith("heal-csv-results-tracker") for x in dscDirFilesStemList):
                messageText = "<br>Warning: It looks like there is no HEAL formatted result tracker in the directory you selected. Are you sure you selected a directory that is a DSC package directory and that you have created a HEAL formatted result tracker? If you have not already created a DSC package directory, you can do so now by navigating to the DSC Package tab in the application, and clicking on the Create sub-tab. This will create a directory called \n'dsc-pkg\n' which will have a HEAL formatted resource tracker and experiment tracker file inside. You can create a HEAL formatted result tracker (please create one per multi-result file - e.g. poster, publication, etc. - you will share) by navigating to the Result Tracker tab, and the Create Result Tracker sub-tab. You may save your result-tracker in your DSC Package directory, but this is not required. Once you've created your DSC Package Directory and created a HEAL formatted Result Tracker, please return here and add your DSC package directory before proceeding to annotate your result(s). While annotating your result(s) you will also need to add the HEAL formatted result tracker you created."
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))

            self.form.widget.state = {
                "result.id": self.result_id
            }

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
            "assoc.file.depends.on": updateAssocFileMultiDepend
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
        
        # check that a dsc data package dir has been added - this is the save folder
        if not self.saveFolderPath:
            messageText = "<br>You must add a DSC Data Package Directory before saving your result file. Please add a DSC Data Package Directory and then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        # check that file path and at least a minimal description has been added to the form 
        # if not exit with informative error
        if not ((self.form.widget.state["assoc.multi.result.file"]) and (self.form.widget.state["description"])):
            messageText = "<br>You must add at least a minimal description of your result and at least one multi-result file in which this result is cited to your result file form before saving your result file. Please add at least a minimal description of your result in the Result Description field in the form, and add at least one multi-result file in which this result appears by browsing to a file path(s) in the Associated Multi-Result File(s) field in the form. Then try saving again." 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        
        # check if user has modified the result id from the one that was autogenerated when adding dsc data dir for saving
        # this may happen if for example a user annotates a result using the autogenerated id, then wants to keep 
        # going using the same form window instance, modify the contents to annotate a new result (perhaps one with some 
        # form fields that will be the same), and save again with a new id - in this case the user can modify the 
        # id manually, incrementing the id number by one - if id modified, updated it in memory and regenerate
        # the save file name, save file path, and id number
        if self.form.widget.state["result.id"] != self.result_id:
            
            self.result_id = self.form.widget.state["result.id"]
            self.resultFileName = 'result-trk-'+ self.result_id + '.txt'
            self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)

            self.resIdNum = int(self.result_id.split("-")[1])
        
        # check if saveFilePath already exists (same as if a file for this resource id already exists); if exists, exit our with informative message;
        # otherwise go ahead and save
        if os.path.isfile(self.saveFilePath):
            messageText = "A result file for a result with id " + self.result_id + " already exists at " + self.saveFilePath + "<br><br>You may want to do one or both of: 1) Use the View/Edit tab to view your result tracker file(s) and check which result IDs you've already used and added to your tracker(s), 2) Use File Explorer to navigate to your DSC Data Package Directory and check which result IDs you've already used and for which you've already created result files - these files will be called \'result-trk-result-{a number}.txt\'. While you perform these checks, your result tracker form will remain open unless you explicitly close it. You can come back to it, change your result ID, and hit the save button again to save with a result ID that is not already in use. If you meant to overwrite a result file you previously created for a result with this result ID, please delete the previously created result file and try saving again.<br><br>" 
            errorFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(errorFormat.format(messageText))
            return

        else:
                              
            result = self.form.widget.state
            f=open(self.saveFilePath,'w')
            print(dumps(result, indent=4), file=f)
            f.close()
                
            #self.messageText = self.messageText + '\n\n' + "Your resource file was successfully written at: " + self.saveFilePath + '\n' + "You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
            messageText = "<br>Your resource was successfully written at: " + self.saveFilePath + "<br><br>You'll want to head back to the \'Add Result\' tab and use the \'Add Result\' button to add this result file to your result tracker file(s)! You can do this now, or later - You can add result files to a result tracker file one at a time, or you can add multiple result files all at once, so you may choose to create result files for several/all of your results and then add them in one go to your result tracker file(s)."
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            self.userMessageBox.moveCursor(QTextCursor.End)

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


        messageText = "<br>Your form was successfully cleared and you can start annotating a new resource"
        saveFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(saveFormat.format(messageText))
        self.userMessageBox.moveCursor(QTextCursor.End)

        messageText = "<br>NOTE: The Result ID in your form has been re-set to the default value of \n'result-1\n'. If you know which result IDs you've already used, you can change the Result ID in the cleared form manually by adding 1 to the max Result ID you've already used. To generate a unique Result ID automatically, click the Add DSC Package Directory button above the form - this will re-add your DSC Package Directory, search that directory for Result IDs already used, generate a unique Result ID by adding 1 to the max Result ID already in use, and add that Result ID value to the form for you."
        saveFormat = '<span style="color:blue;">{}</span>'
        self.userMessageBox.append(saveFormat.format(messageText)) 
        self.userMessageBox.moveCursor(QTextCursor.End)           

             

        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateResultWindow()
    window.show()
    sys.exit(app.exec_())