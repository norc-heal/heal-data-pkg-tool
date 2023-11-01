import sys
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, uic
import dsc_pkg_utils


#class Window(QWidget):
class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.initUI()

        
    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        
        ################################## Create component widgets 
        
        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)

        self.labelUserMessageBox = QtWidgets.QLabel(text = "User Status Message Box:", parent=self)

        # self.labelAddMultiDepend.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        # )
        # self.labelAddMultiDepend.setWordWrap(True)

        self.listCheckBox = ["Checkbox_1", "Checkbox_2", "Checkbox_3", "Checkbox_4", "Checkbox_5",
                             "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10",
                             "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10",
                             "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10" ]
        self.listPushButton    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ] 
        self.listLabel    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ]
        self.grid = QGridLayout()

        self.checkboxLabel = QLabel("<b>Share resource?</b>")
        self.grid.addWidget(self.checkboxLabel,0,0)

        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listPushButton[i] = QPushButton("Add resource to tracker")
            self.listLabel[i] = QLabel()
            self.grid.addWidget(self.listCheckBox[i], i+1, 0)
            self.grid.addWidget(self.listPushButton[i], i+1, 1)
            self.grid.addWidget(self.listLabel[i],    i+1, 2)

        self.button = QPushButton("Check CheckBox")
        self.button.clicked.connect(self.checkboxChanged)
        self.labelResult = QLabel()

        self.grid.addWidget(self.button,     len(self.listCheckBox) + 1, 0, 1,2)     
        self.grid.addWidget(self.labelResult,len(self.listCheckBox) + 2, 0, 1,2)  
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
        
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
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
        

    def checkboxChanged(self):
        self.labelResult.setText("")
        for i, v in enumerate(self.listCheckBox):
            self.listLabel[i].setText("True" if v.checkState() else "False")
            self.labelResult.setText("{}, {}".format(self.labelResult.text(),
                                                     self.listLabel[i].text()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())