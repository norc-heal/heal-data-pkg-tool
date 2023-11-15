import sys
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import dsc_pkg_utils

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.listCheckBox = ["Checkbox_1", "Checkbox_2", "Checkbox_3", "Checkbox_4", "Checkbox_5",
                             "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10",
                             "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10",
                             "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10" ]
        self.listPushButton    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ] 
        self.listLabel    = ['', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '', '', ]
        grid = QGridLayout()

        self.checkboxLabel = QLabel("<b>Share resource?</b>")
        grid.addWidget(self.checkboxLabel,0,0)

        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listPushButton[i] = QPushButton("Add resource to tracker")
            self.listLabel[i] = QLabel()
            grid.addWidget(self.listCheckBox[i], i+1, 0)
            grid.addWidget(self.listPushButton[i], i+1, 1)
            grid.addWidget(self.listLabel[i],    i+1, 2)

        self.button = QPushButton("Check CheckBox")
        self.button.clicked.connect(self.checkboxChanged)
        self.labelResult = QLabel()

        grid.addWidget(self.button,     len(self.listCheckBox) + 1, 0, 1,2)     
        grid.addWidget(self.labelResult,len(self.listCheckBox) + 2, 0, 1,2)  
        self.setLayout(grid)        

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