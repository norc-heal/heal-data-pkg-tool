import sys
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, uic
import dsc_pkg_utils
from pathlib import Path # base python, no pip install needed
from PyQt5.QtCore import Qt, QSize
import os
import pandas as pd
from layout_scrollannotateresourcewidget import ScrollAnnotateResourceWindow


#class Window(QWidget):
class ResourcesToAddWindow(QtWidgets.QMainWindow):
    def __init__(self, workingDataPkgDirDisplay, parent=None):
        super(ResourcesToAddWindow, self).__init__(parent)
        #self.workingDataPkgDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.w = None  # No external window yet.
        
        self.grid = None
        self.newSession = True

        self.shareStatusListChanged = False
        self.annotationModeChanged = False

        self.shareStatusList = []
        self.shareStatusDf = []
        self.annotationModeStatus = None
        
        self.initUI()

    
    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        
        ################################## Create component widgets 
        
        self.buttonLoadList = QtWidgets.QPushButton("Load Resource List")
        self.buttonLoadList.clicked.connect(self.loadResourceList)

        self.buttonUpdateList = QtWidgets.QPushButton("Update Resource List")

        # create status message box
        self.labelUserMessageBox = QtWidgets.QLabel(text = "User Status Message Box:", parent=self)

        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)

        self.labelMinimalAnnotationCheckbox = QtWidgets.QLabel(text = "<b>Have you chosen a minimal annotation standard due to a very low level of resources available to devote to data-sharing?</b>", parent=self)
        self.minimalAnnotationCheckbox = QtWidgets.QCheckBox("Yes, I have chosen a minimal annotation standard")
        self.minimalAnnotationCheckbox.setChecked(False)
        #self.minimalAnnotationCheckbox.stateChanged.connect(self.checkIfMinimalAnnotation)

        # start hidden - unhide when user loads list of resources to add
        self.labelMinimalAnnotationCheckbox.hide()
        self.minimalAnnotationCheckbox.hide()
        
        # self.listCheckBox    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ]
        # self.listPath    = ['my-file.csv']*20
        # self.listType    = ['associatedDataDictionary']*20
        # self.listParent    = ['resource-1']*20
        # self.listPushButton    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ] 
        # self.listPushButton2    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ] 
        # self.listLabel    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ]
        # self.grid = QGridLayout()

        # self.checkboxLabel = QLabel("<b>Share resource?</b>")
        # self.checkboxLabel.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.checkboxLabel.setWordWrap(True)
        # self.grid.addWidget(self.checkboxLabel,0,0,Qt.AlignCenter)
        # # start hidden
        # self.checkboxLabel.hide()

        # self.pathLabel = QLabel("<b>Path</b>")
        # self.pathLabel.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.pathLabel.setWordWrap(True)
        # self.grid.addWidget(self.pathLabel,0,1,Qt.AlignCenter)

        # self.typeLabel = QLabel("<b>Type</b>")
        # self.typeLabel.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.typeLabel.setWordWrap(True)
        # self.grid.addWidget(self.typeLabel,0,2,Qt.AlignCenter)

        # self.parentLabel = QLabel("<b>Parent</b>")
        # self.parentLabel.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.parentLabel.setWordWrap(True)
        # self.grid.addWidget(self.parentLabel,0,3,Qt.AlignCenter)

        # for i, v in enumerate(self.listCheckBox):
        #     self.listCheckBox[i] = QCheckBox(v)
        #     self.listCheckBox[i].setChecked(True) 
        #     self.listCheckBox[i].stateChanged.connect(self.updateActionButton)
        #     # start hidden
        #     self.listCheckBox[i].hide()

        #     self.listPath[i] = QLabel(self.listPath[i])
        #     self.listType[i] = QLabel(self.listType[i])
        #     self.listParent[i] = QLabel(self.listParent[i])
        #     self.listPushButton[i] = QPushButton("Add resource to tracker")
            
        #     self.listPushButton2[i] = QPushButton("Rapid audit resource")
        #     # start hidden
        #     self.listPushButton2[i].hide()
            
            
        #     self.grid.addWidget(self.listCheckBox[i], i+1, 0, Qt.AlignCenter)
        #     self.grid.addWidget(self.listPath[i],    i+1, 1, Qt.AlignCenter)
        #     self.grid.addWidget(self.listType[i],    i+1, 2, Qt.AlignCenter)
        #     self.grid.addWidget(self.listParent[i],    i+1, 3, Qt.AlignCenter)
        #     self.grid.addWidget(self.listPushButton[i], i+1, 4)
        #     self.grid.addWidget(self.listPushButton2[i], i+1, 5)
       
        ################################## Finished creating component widgets - add them to vbox layout
        
        self.vbox.addWidget(self.buttonLoadList)
        self.vbox.addWidget(self.buttonUpdateList)
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
        self.vbox.addWidget(self.labelMinimalAnnotationCheckbox, Qt.AlignCenter)
        self.vbox.addWidget(self.minimalAnnotationCheckbox, Qt.AlignCenter)
        #self.vbox.addLayout(self.grid)
        
        ################################## Set layout of the grouping widget as the vbox layout with widgets added

        self.widget.setLayout(self.vbox)

        ################################## Set widget of the scroll area as the grouping widget 
        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        ################################## Set scroll area as central widget 
        self.setCentralWidget(self.scroll)
        #self.setLayout(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle("Annotate Resource")
        

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
        
    def loadResourceList(self):

        self.loadingFile = True
        print("loading resource list")
        
        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # these conditions will only be true if the user has alreay loaded a resource list at least once, 
        # this means the check on working data pkg dir set will already be done, so this does not need to be 
        # run after checking for working data pkg dir set again, but just to be safe..
        if ((self.shareStatusListChanged) | (self.annotationModeChanged)):
            # if user has changed the status of either the share status check boxes or the minimal annotation mode check box, 
            # write the share status list and annotation mode status to file, then reset the changed boolean vars back to false
            # to be ready to detect a new change to either of these
            self.cleanup()

        # resource tracker and resources to add files are needed to populate the list of resources that need to be added so perform some checks
        checkFileList = ["heal-csv-resource-tracker.csv","resources-to-add.csv"]
        checkFileNameList = ["Resource Tracker","Resources-to-Add"]

        for i,c in enumerate(checkFileList):
            # check that file exists in working data pkg dir, if not, return
            if not os.path.exists(os.path.join(self.workingDataPkgDir, c)):
                messageText = "<br>There is no " + checkFileNameList[i] + " file in your working Data Package Directory; Your working Data Package Directory must contain a " +  checkFileNameList[i] + " file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return
            
            # check that file is closed (user doesn't have it open in excel for example)
            try: 
                with open(os.path.join(self.workingDataPkgDir, c),'r+') as f:
                    print("file is closed, proceed!!")
            except PermissionError:
                    messageText = "<br>The " + checkFileNameList[i] + " file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the " + checkFileNameList[i] + " file is open in Excel or similar application, and close the file. <br>"
                    saveFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    return
        
        ##############################################################################################

        resourcePathList = dsc_pkg_utils.get_added_resource_paths(self=self)
        
        if not resourcePathList:
                   
            messageText = "<br>We can't currently populate a list of study files/resources that need to be added to the Resource Tracker. The list of study files/resources you still need to add to your Resource Tracker is populated by pulling in study files/resources you have listed as associated/dependencies for resources you have already added to the Resource Tracker. <br><br>You have not added any study files/resources to the Resource Tracker in your working Data Package Directory. You must add at least one study file/resource to the Resource Tracker to proceed. For guidance on where to start (e.g. which study file/resource to start with) you can visit the <a href=\"https://norc-heal.github.io/heal-data-pkg-guide/\">HEAL Data Packaging Guide</a>. To add a first study resource/file to your Resource Tracker, navigate to the \"Resource Tracker\" tab >> \"Add Resource\" sub-tab and click on the \"Add a new resource\" push-button. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

        resourcesToAddDf = dsc_pkg_utils.get_resources_to_add(self=self)

        if ((not isinstance(resourcesToAddDf, pd.DataFrame)) | resourcesToAddDf.empty):
             
            messageText = "<br>We can't currently populate a list of study files/resources that need to be added to the Resource Tracker. The list of study files/resources you still need to add to your Resource Tracker is populated by pulling in study files/resources you have listed as associated/dependencies for resources you have already added to the Resource Tracker. <br><br>You have not listed any files as associated/dependencies for any of the study files/resources you've already added to the Resource Tracker in your working Data Package Directory. You must add at least one file that is an associated file/dependency for a study file/resource added to the Resource Tracker to proceed. For guidance on where to start (e.g. which study file/resource to start with) you can visit the <a href=\"https://norc-heal.github.io/heal-data-pkg-guide/\">HEAL Data Packaging Guide</a> site. To add a first study resource/file to your Resource Tracker, navigate to the \"Resource Tracker\" tab >> \"Add Resource\" sub-tab and click on the \"Add a new resource\" push-button. For guidance on how to add an associated file/dependency for a study file/resource when you add it to the Resource tracker, head to the <a href=\"https://norc-heal.github.io/heal-data-pkg-tool-docs/\">HEAL Data Packaging Tool \"How-to\" </a> site<br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

        print(resourcesToAddDf.shape)
        # remove resources already added to resource tracker from list
        resourcesToAddDf = resourcesToAddDf[~resourcesToAddDf["path"].isin(resourcePathList)]
        print("removed resources already added:")
        print(resourcesToAddDf.shape)

        # sort by date-time (ascending), then drop duplicates of resource that needs to be added, keeping the first/earliest instance 
        resourcesToAddDf.sort_values(by=["date-time"],ascending=True,inplace=True)
        resourcesToAddDf.drop_duplicates(subset=["path"],inplace=True)
        print("drop duplicates of resource that needs to be added, keep the first instance:")
        print(resourcesToAddDf.shape)

        
        

        
        #################################################################################################
        # if grid layout already exists, delete it before remaking and readding to vbox layout
        if self.grid: 
            print("deleting existing grid layout")
            dsc_pkg_utils.layoutInLayoutDelete(containerLayout=self.vbox,layoutInLayout=self.grid)
        #################################################################################################

        self.labelMinimalAnnotationCheckbox.show() 
        self.minimalAnnotationCheckbox.show()
                        
        self.listCheckBox    = ['']*resourcesToAddDf.shape[0]
        self.listPath    = resourcesToAddDf["path"].tolist()
        self.listType    = resourcesToAddDf["dependency-type"].tolist()
        self.listParent    = resourcesToAddDf["parent-resource-id"].tolist()
        self.listPushButton    = ['']*resourcesToAddDf.shape[0]
        self.listPushButton2    = ['']*resourcesToAddDf.shape[0]
        self.grid = QGridLayout()

        self.checkboxLabel = QLabel("<b>Share resource?</b>")
        self.checkboxLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.checkboxLabel.setWordWrap(True)
        self.grid.addWidget(self.checkboxLabel,0,0,Qt.AlignCenter)
        # start hidden
        self.checkboxLabel.hide()

        self.pathLabel = QLabel("<b>Path</b>")
        self.pathLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.pathLabel.setWordWrap(True)
        self.grid.addWidget(self.pathLabel,0,1,Qt.AlignCenter)

        self.typeLabel = QLabel("<b>Type</b>")
        self.typeLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.typeLabel.setWordWrap(True)
        self.grid.addWidget(self.typeLabel,0,2,Qt.AlignCenter)

        self.parentLabel = QLabel("<b>Parent</b>")
        self.parentLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.parentLabel.setWordWrap(True)
        self.grid.addWidget(self.parentLabel,0,3,Qt.AlignCenter)

        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listCheckBox[i].setChecked(True) 
            
            #self.listCheckBox[i].stateChanged.connect(self.updateActionButton)
            # start hidden
            self.listCheckBox[i].hide()

            self.listPath[i] = QLabel(self.listPath[i])
            self.listType[i] = QLabel(self.listType[i])
            self.listParent[i] = QLabel(self.listParent[i])
            self.listPushButton[i] = QPushButton("Add resource to tracker")
            
            self.listPushButton2[i] = QPushButton("Rapid audit resource")
            # start hidden
            self.listPushButton2[i].hide()
            
            self.grid.addWidget(self.listCheckBox[i], i+1, 0, Qt.AlignCenter)
            self.grid.addWidget(self.listPath[i],    i+1, 1, Qt.AlignCenter)
            self.grid.addWidget(self.listType[i],    i+1, 2, Qt.AlignCenter)
            self.grid.addWidget(self.listParent[i],    i+1, 3, Qt.AlignCenter)
            self.grid.addWidget(self.listPushButton[i], i+1, 4)
            self.grid.addWidget(self.listPushButton2[i], i+1, 5)
            
        ################################## Finished creating component widgets - add them to vbox layout
        
        self.vbox.addLayout(self.grid)
                        
        ################################## Update default settings of minimal annotation checkbox and share status checkboxes based on information either from this or previous/most recent session
        if os.path.isfile(os.path.join(self.workingDataPkgDir,"latest-share-status.csv")):
            self.annotationModeStatus = dsc_pkg_utils.get_resources_annotation_mode_status(self=self)
            print("annotationModeStatus from file: ",self.annotationModeStatus)
        
        # by default, minimal annotation box is unchecked
        # if user set annotation to minimal, check it
        if self.annotationModeStatus:
            if self.annotationModeStatus == "minimal":
                print("setting minimal annotation status from previous knowledge")
                self.minimalAnnotationCheckbox.setChecked(True) 

        if os.path.isfile(os.path.join(self.workingDataPkgDir,"share-status.csv")):
            self.shareStatusDf = dsc_pkg_utils.get_resources_share_status(self=self)
            print("shareStatusDf from file: ",self.shareStatusDf)

        # by default, share status checkboxes are checked
        # if user set share status to not share, uncheck it
        if isinstance(self.shareStatusDf,pd.DataFrame):
            for i, v in enumerate(self.listCheckBox):
                if self.listPath[i].text() in self.shareStatusDf["path"].values:
                #if (self.shareStatusDf["path"] == self.listPath[i].text()).any():
                    print ("Share status available for: ", self.listPath[i].text())
                    subShareStatusDf = self.shareStatusDf[self.shareStatusDf["path"] == self.listPath[i].text()]
                    print(subShareStatusDf)
                    print(subShareStatusDf.shape) # should be just one row

                    if subShareStatusDf["share-status"].iloc[0] != "share":
                        self.listCheckBox[i].setChecked(False) 

        # calling this function will check if the minimal annotation checkbox is checked
        # if it is this will 1) unhide the share status checkboxes, and 2) call the self.updateActionButton() fx
        # which will check if each share status box is checked and if it is will show just the add resource to tracker button
        # for that resource, and if it is not will show just the rapid audit resource button for that resource
        self.checkIfMinimalAnnotation()
        #
        #self.updateActionButton()
        
        ################################## Hook up checkboxes to signal connect function after set up is complete
        self.minimalAnnotationCheckbox.stateChanged.connect(self.checkIfMinimalAnnotation)
        
        self.formSetStateList = []

        for i, v in enumerate(self.listCheckBox):
            
            self.listCheckBox[i].stateChanged.connect(self.updateActionButton)
            #self.listPushButton[i].clicked.connect(self.annotate_resource)
            #self.listPushButton[i].clicked.connect(lambda gridLayoutIndex: self.annotate_resource(i))

            formSetState = {}

            setPath = self.listPath[i].text() 
            setType = self.listType[i].text()  
            setParent = self.listParent[i].text() 
            print("setPath: ", setPath)
            print("setType: ", setType)
            print("setParent: ", setParent)

            if setType in ["associatedFileDataDict","associatedFileProtocol","associatedFileResultsTracker"]:
                setCategory = "metadata"
                if setType == "associatedFileProtocol":
                    setCategorySubMetadata = "protocol"
                    setDescription = "protocol for " + setParent
                elif setType == "associatedFileResultsTracker":
                    setCategorySubMetadata = "heal-formatted-results-tracker"
                    setDescription = "heal formatted results tracker for " + setParent
                elif setType == "associatedFileDataDict":
                    setCategorySubMetadata = "heal-formatted-data-dictionary"
                    setDescription = "heal formatted data dictionary for " + setParent 
            else:
                setCategory = ""
                setCategorySubMetadata = ""
                setDescription = ""
            
            formSetState = {
                "path": setPath,
                "description": setDescription,
                "category": setCategory,
                "categorySubMetadata": setCategorySubMetadata
            }
            self.formSetStateList.append(formSetState)
            print("formSetState: ", formSetState)
            #self.listPushButton[i].clicked.connect(lambda formSetState: self.annotate_resource(formSetStateValue))
            #self.listPushButton[i].clicked.connect(self.annotate_resource((lambda formSetState: lambda: formSetState)(formSetStateValue)))
            #self.listPushButton[i].clicked.connect(lambda formSetState=formSetState: self.annotate_resource(formSetState))
            #self.listPushButton[i].clicked.connect(lambda x=formSetState: self.annotate_resource(x))
            #self.listPushButton[i].clicked.connect(lambda formSetState: self.annotate_resource(x)) # passes last
            self.listPushButton[i].clicked.connect(lambda x=formSetState: self.annotate_resource(formSetState=x)) # passes nothing
            

        ################################## Set share status and annotation mode changed signals back to false after set up is complete        
        
        self.shareStatusListChanged = False
        self.annotationModeChanged = False

        #self.shareStatusList = []
        #self.shareStatusDf = []
        #self.annotationModeStatus = None
        
        # self.newSession = False # set new session indicator to False - this will let the widget know that it shouldn't try to open share status or annotation mode status save files, but should load them from local within session vars if they exist
        # self.loadFileStatus = True
        self.loadingFile = False
        print("done loading resource list")

    # def deleteItemsOfLayout(layout):
    #     if layout is not None:
    #         while layout.count():
    #             item = layout.takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 widget.setParent(None)
    #             else:
    #                 deleteItemsOfLayout(item.layout())

    # def layoutInLayoutDelete(self, layoutInLayout):
    #     for i in range(self.containerLayout.count()):
    #         layout_item = self.containerLayout.itemAt(i)
    #         if layout_item.layout() == layoutInLayout:
    #             deleteItemsOfLayout(layout_item.layout())
    #             self.containerLayout.removeItem(layout_item)
    #             break
    
    def updateActionButton(self):
        print("something happened")

        # # this update action will get triggered during load file fx; return if checkboxes are being updated by load file function
        # if self.loadingFile:
        #     print("share status changed while loading file - ignore change")
        #     return

        #print("share status changed outside of loading file - DO NOT ignore change")
        print("start self.shareStatusList: ", self.shareStatusList)
        startShareStatusList = self.shareStatusList
        self.shareStatusListChanged = True
        self.shareStatusList = []
        self.pathShareStatusList = []
       

        for i, v in enumerate(self.listCheckBox):
            self.pathShareStatusList.append(self.listPath[i].text())
            #print(self.pathShareStatusList)

            if self.listCheckBox[i].isChecked():
                self.shareStatusList.append("share")
                self.listPushButton[i].show()
                self.listPushButton2[i].hide()
            else:
                self.shareStatusList.append("no-share")
                self.listPushButton[i].hide()
                self.listPushButton2[i].show()

        #print("end self.pathShareStatusList: ", self.pathShareStatusList)
        print("start self.shareStatusList: ", startShareStatusList)
        print("end self.shareStatusList: ", self.shareStatusList)


        if self.shareStatusList == startShareStatusList: 
            self.shareStatusListChanged = False
        
        print("self.shareStatusListChanged: ", self.shareStatusListChanged)


    def checkIfMinimalAnnotation(self):
        print("annotation mode changed")
        print("start self.annotationModeStatus: ", self.annotationModeStatus)
        self.annotationModeChanged = True
        self.annotationModeStatus = None

        if self.minimalAnnotationCheckbox.isChecked():
            self.annotationModeStatus = "minimal"
            self.checkboxLabel.show()
            for i, v in enumerate(self.listCheckBox):
            
                # start hidden
                self.listCheckBox[i].show()

                # if self.listCheckBox[i].isChecked:
                #     self.listPushButton[i].show()
                #     self.listPushButton2[i].hide()
                # else: 
                #     self.listPushButton[i].hide()
                #     self.listPushButton2[i].show()

            self.updateActionButton()

        else:
            self.annotationModeStatus = "standard-wholistic"
            self.checkboxLabel.hide()
            for i, v in enumerate(self.listCheckBox):
            
                # start hidden
                self.listCheckBox[i].hide()
            
                # start hidden
                self.listPushButton2[i].hide()

                self.listPushButton[i].show()

        print("end self.annotationModeStatus: ", self.annotationModeStatus)

    def cleanup(self):
        
        if self.shareStatusListChanged:
            self.shareStatusDf = pd.DataFrame(list(zip(self.pathShareStatusList, self.shareStatusList)),
               columns =["path", "share-status"])
            self.shareStatusDf["date-time"] = pd.Timestamp("now")
            
            # if there's already an existing share status df written to file, append the one from this call
            if os.path.isfile(os.path.join(self.workingDataPkgDir,"share-status.csv")):
                existingShareStatusDf = pd.read_csv(os.path.join(self.workingDataPkgDir,"share-status.csv"))
                pd.to_datetime(existingShareStatusDf["date-time"])
                print(existingShareStatusDf.shape) 
                
                self.shareStatusDf = pd.concat([existingShareStatusDf,self.shareStatusDf],axis=0)
            
            self.shareStatusDf.to_csv(os.path.join(self.workingDataPkgDir,"share-status.csv"), index=False)

            self.shareStatusListChanged = False

        if self.annotationModeChanged:
            print("hello")
            df = pd.DataFrame([self.annotationModeStatus], columns =['annotation-mode-status'])
            df["date-time"] = pd.Timestamp("now")

            # if there's already an existing annotation mode status df written to file, append the one from this call
            if os.path.isfile(os.path.join(self.workingDataPkgDir,"annotation-mode-status.csv")):
                existingAnnotationModeStatusDf = pd.read_csv(os.path.join(self.workingDataPkgDir,"annotation-mode-status.csv"))
                pd.to_datetime(existingAnnotationModeStatusDf["date-time"])
                print(existingAnnotationModeStatusDf.shape) 
                
                df = pd.concat([existingAnnotationModeStatusDf,df],axis=0)

            df.to_csv(os.path.join(self.workingDataPkgDir,"annotation-mode-status.csv"), index=False)

            self.annotationModeChanged = False

    def annotate_resource(self, formSetState={}):

        print("in annotate resource fx")

        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

        # experiment tracker is needed to populate the enum of experimentNameBelongsTo schema property so perform some checks

        # check that experiment tracker exists in working data pkg dir, if not, return
        if not os.path.exists(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv")):
            messageText = "<br>There is no Experiment Tracker file in your working Data Package Directory; Your working Data Package Directory must contain an Experiment Tracker file to proceed. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return
        
        # check that experiment tracker is closed (user doesn't have it open in excel for example)
        try: 
            with open(os.path.join(self.workingDataPkgDir,"heal-csv-experiment-tracker.csv"),'r+') as f:
                print("file is closed, proceed!!")
        except PermissionError:
                messageText = "<br>The Experiment Tracker file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the Experiment Tracker file is open in Excel or similar application, and close the file. <br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

        # ######################################### Get the path, type, and parent resource id
        # setPath = self.listPath[gridLayoutIndex].text() 
        # setType = self.listType[gridLayoutIndex].text()  
        # setParent = self.listParent[gridLayoutIndex].text() 

        # if setType in ["associatedFileDataDict","associatedFileProtocol","associatedFileResultsTracker"]:
        #     setCategory = "metadata"
        #     if setType == "associatedFileProtocol":
        #         setCategorySubMetadata = "protocol"
        #         setDescription = "protocol for " + setParent
        #     elif setType == "associatedFileResultsTracker":
        #         setCategorySubMetadata = "heal-formatted-results-tracker"
        #         setDescription = "heal formatted results tracker for " + setParent
        #     elif setType == "associatedFileDataDict":
        #         setCategorySubMetadata = "heal-formatted-data-dictionary"
        #         setDescription = "heal formatted data dictionary for " + setParent 
        # else:
        #     setCategory = ""
        #     setCategorySubMetadata = ""
        #     setDescription = ""
        
        # formSetState = {
        #     "path": setPath,
        #     "description": setDescription,
        #     "category": setCategory,
        #     "categorySubMetadata": setCategorySubMetadata
        # }
        
        print("formSetState passed to annotate resource fx: ",formSetState)
        
        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            #self.w.editState = False
            self.w = ScrollAnnotateResourceWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, workingDataPkgDir=self.workingDataPkgDir, mode="add",formSetState=formSetState)
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    # def checkboxChanged(self):
    #     self.labelResult.setText("")
    #     for i, v in enumerate(self.listCheckBox):
    #         self.listLabel[i].setText("True" if v.checkState() else "False")
    #         self.labelResult.setText("{}, {}".format(self.labelResult.text(),
    #                                                  self.listLabel[i].text()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = ResourcesToAddWindow()
    clock.show()
    sys.exit(app.exec_())