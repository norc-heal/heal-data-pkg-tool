import sys
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, uic
import dsc_pkg_utils
from pathlib import Path # base python, no pip install needed
from PyQt5.QtCore import Qt, QSize


#class Window(QWidget):
class ResourcesToAddWindow(QtWidgets.QMainWindow):
    def __init__(self, workingDataPkgDirDisplay, parent=None):
        super(ResourcesToAddWindow, self).__init__(parent)
        #self.workingDataPkgDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.initUI()

        
    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        
        ################################## Create component widgets 
        
        self.buttonLoadList = QtWidgets.QPushButton("Load Resource List")
        self.buttonUpdateList = QtWidgets.QPushButton("Update Resource List")

        # create status message box
        self.labelUserMessageBox = QtWidgets.QLabel(text = "User Status Message Box:", parent=self)

        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)

        self.labelMinimalAnnotationCheckbox = QtWidgets.QLabel(text = "<b>Have you chosen a minimal annotation standard due to a very low level of resources available to devote to data-sharing?</b>", parent=self)
        self.minimalAnnotationCheckbox = QtWidgets.QCheckBox("Yes, I have chosen a minimal annotation standard")
        self.minimalAnnotationCheckbox.stateChanged.connect(self.checkIfMinimalAnnotation)
        
        # self.labelAddMultiDepend.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.labelAddMultiDepend.setWordWrap(True)

        # self.listCheckBox = ["Checkbox_1", "Checkbox_2", "Checkbox_3", "Checkbox_4", "Checkbox_5",
        #                      "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10",
        #                      "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10",
        #                      "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10" ]
        self.listCheckBox    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ]
        self.listPath    = ['my-file.csv']*20
        self.listType    = ['associatedDataDictionary']*20
        self.listParent    = ['resource-1']*20
        self.listPushButton    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ] 
        self.listPushButton2    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ] 
        self.listLabel    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ]
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
            self.listCheckBox[i].stateChanged.connect(self.updateActionButton)
            # start hidden
            self.listCheckBox[i].hide()

            self.listPath[i] = QLabel(self.listPath[i])
            self.listType[i] = QLabel(self.listType[i])
            self.listParent[i] = QLabel(self.listParent[i])
            self.listPushButton[i] = QPushButton("Add resource to tracker")
            
            self.listPushButton2[i] = QPushButton("Rapid audit resource")
            # start hidden
            self.listPushButton2[i].hide()
            
            #self.listLabel[i] = QLabel()
            self.grid.addWidget(self.listCheckBox[i], i+1, 0, Qt.AlignCenter)
            self.grid.addWidget(self.listPath[i],    i+1, 1, Qt.AlignCenter)
            self.grid.addWidget(self.listType[i],    i+1, 2, Qt.AlignCenter)
            self.grid.addWidget(self.listParent[i],    i+1, 3, Qt.AlignCenter)
            self.grid.addWidget(self.listPushButton[i], i+1, 4)
            self.grid.addWidget(self.listPushButton2[i], i+1, 5)
            #self.grid.addWidget(self.listLabel[i],    i+1, 5)

        #self.button = QPushButton("Check CheckBox")
        #self.button.clicked.connect(self.checkboxChanged)
        #self.labelResult = QLabel()

        #self.grid.addWidget(self.button,     len(self.listCheckBox) + 1, 0, 1,2)     
        #self.grid.addWidget(self.labelResult,len(self.listCheckBox) + 2, 0, 1,2) 
        # self.grid.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # ) 
        #self.setLayout(grid)

        
       
        # ################################## Apply some initializing and maintenance functions

        # # initialize tool tip for each form field based on the description text for the corresponding schema property
        # self.add_tooltip()
        # self.add_priority_highlight_and_hide()
        # self.add_dir()
        # if self.mode == "add":
        #     self.get_id()
        # #self.add_priority_highlight()
        # #self.initial_hide()
        # self.popFormField = []
        # self.editSingle = False

        # # check for emptyp tooltip content whenever form changes and replace empty tooltip with original tooltip content
        # # (only relevant for fields with in situ validation - i.e. string must conform to a pattern - as pyqtschema will replace the 
        # # tooltip content with some error content, then replace the content with empty string once the error is cleared - this check will
        # # restore the original tooltip content - for efficiency, may want to only run this when a widget that can have validation 
        # # errors changes - #TODO)
        # self.form.widget.on_changed.connect(self.check_tooltip)
        # self.formWidgetList[self.formWidgetNameList.index("category")].on_changed.connect(self.conditional_fields)
        # self.formWidgetList[self.formWidgetNameList.index("access")].on_changed.connect(self.conditional_fields)
        # self.formWidgetList[self.formWidgetNameList.index("descriptionFileNameConvention")].on_changed.connect(self.conditional_highlight_apply_convention)
        # self.formWidgetList[self.formWidgetNameList.index("categorySubMetadata")].on_changed.connect(self.conditional_fields)
        # self.formWidgetList[self.formWidgetNameList.index("path")].on_changed.connect(self.conditional_fields)
        
        
        
        ################################## Finished creating component widgets - add them to vbox layout
        
        self.vbox.addWidget(self.buttonLoadList)
        self.vbox.addWidget(self.buttonUpdateList)
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
        self.vbox.addWidget(self.labelMinimalAnnotationCheckbox, Qt.AlignCenter)
        self.vbox.addWidget(self.minimalAnnotationCheckbox, Qt.AlignCenter)
        self.vbox.addLayout(self.grid)
        
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
        # check if user has set a working data package dir - if not exit gracefully with informative message
        if not dsc_pkg_utils.getWorkingDataPkgDir(self=self):
            return

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

        if dsc_pkg_utils.get_added_resource_paths(self=self):
            print("do a thing")
        else: 
            messageText = "<br>The list of study files/resources you still need to add to your Resource Tracker is populated by pulling in study files/resources you have listed as associated/dependencies for resources you have already added to the Resource Tracker. <br><br>You have not added any study files/resources to the Resource Tracker in your working Data Package Directory. You must add at least one study file/resource to the Resource Tracker to proceed. For guidance on where to start (e.g. which study file/resource to start with) you can visit the <a href=\"https://norc-heal.github.io/heal-data-pkg-guide/\">HEAL Data Packaging Guide</a>. To add a first study resource/file to your Resource Tracker, navigate to the \"Resource Tracker\" tab >> \"Add Resource\" sub-tab and click on the \"Add a new resource\" push-button. <br>"
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))





    def updateActionButton(self):
        #check = self.checkbox.isChecked() 
        print("something happened")
        for i, v in enumerate(self.listCheckBox):
            if self.listCheckBox[i].isChecked():
                self.listPushButton[i].show()
                self.listPushButton2[i].hide()
            else:
                self.listPushButton[i].hide()
                self.listPushButton2[i].show()



    def checkIfMinimalAnnotation(self):
        print("annotation mode changed")
        if self.minimalAnnotationCheckbox.isChecked():
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
            self.checkboxLabel.hide()
            for i, v in enumerate(self.listCheckBox):
            
                # start hidden
                self.listCheckBox[i].hide()
            
                # start hidden
                self.listPushButton2[i].hide()

                self.listPushButton[i].show()



    def checkboxChanged(self):
        self.labelResult.setText("")
        for i, v in enumerate(self.listCheckBox):
            self.listLabel[i].setText("True" if v.checkState() else "False")
            self.labelResult.setText("{}, {}".format(self.labelResult.text(),
                                                     self.listLabel[i].text()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = ResourcesToAddWindow()
    clock.show()
    sys.exit(app.exec_())