#https://realpython.com/python-pyqt-layout/#:~:text=addTab()%20%2C%20then%20that%20icon,layout%20containing%20the%20required%20widgets.

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from layout_pkgcreatewidget import PkgCreateWindow
from layout_infotextwidget import InfoTextWindow
from layout_csvpushtoloadwidget import CSVPushToLoadWindow


        

class PkgTabsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Package")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "Start your data packaging and submission journey by creating a DSC Data Package directory! By creating your DSC Data Package directory and following the recommendations and process flow for data packaging set forth in the Data Packaging Recommendations and Process Flow document, you'll memorialize what each data and non-data/supporting file in your study data package is/represents, how these files related to each other, and how to drill down into these componenet data and non-data/supporting files to recreate specific published results. This will facilitate continuity and passed-down knowledge within study groups, and discovery, sharing, and re-use of the data and knowledge produced by the study outside of the original study group."
        
        
        # Create the tab widget 
        tabs = QTabWidget()
        tabs.addTab(InfoTextWindow(infoText=self.infoText), "Info")
        tabs.addTab(PkgCreateWindow(), "Create")
        #tabs.addTab(CSVPushToLoadWindow(), "View/Edit")
        
        layout.addWidget(tabs)

        

    def generalTabUI(self):
        """Create the General page UI."""
        generalTab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("General Option 1"))
        layout.addWidget(QCheckBox("General Option 2"))
        generalTab.setLayout(layout)
        return generalTab

    def networkTabUI(self):
        """Create the Network page UI."""
        networkTab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("Network Option 1"))
        layout.addWidget(QCheckBox("Network Option 2"))
        networkTab.setLayout(layout)
        return networkTab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PkgTabsWindow()
    window.show()
    sys.exit(app.exec_())



