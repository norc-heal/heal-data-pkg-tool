#https://realpython.com/python-pyqt-layout/#:~:text=addTab()%20%2C%20then%20that%20icon,layout%20containing%20the%20required%20widgets.

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

#from layout_vlmdinfowidget import VLMDInfoWindow
from layout_infotextwidget import InfoTextWindow
from layout_vlmdcreatewidget import VLMDCreateWindow
from layout_csvpushtoloadwidget import CSVPushToLoadWindow
from layout_vlmdvalidatewidget import VLMDValidateWindow

class VLMDTabsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Dictionary")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "You should create a data dictionary for every tabular or tabular-like data file you collect/share as part of your study. This allows you to memorialize what each variable in your dataset is/represents, what values it can take on, etc. This will facilitate continuity and passed-down knowledge within study groups, and sharing and re-use of the data outside of the original study group."
        
        # Create the tab widget 
        tabs = QTabWidget()
        tabs.addTab(InfoTextWindow(infoText=self.infoText), "Info")
        tabs.addTab(VLMDCreateWindow(), "Create")
        tabs.addTab(VLMDValidateWindow(), "Validate")
        tabs.addTab(CSVPushToLoadWindow(), "View/Edit")
        layout.addWidget(tabs)

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VLMDTabsWindow()
    window.show()
    sys.exit(app.exec_())



