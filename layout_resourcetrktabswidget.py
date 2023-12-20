#https://realpython.com/python-pyqt-layout/#:~:text=addTab()%20%2C%20then%20that%20icon,layout%20containing%20the%20required%20widgets.

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

#from layout_vlmdcreatewidget import VLMDCreateWindow
#from layout_exptrkaddwidget import ExpTrkAddWindow
from layout_resourcetrkaddwidget import ResourceTrkAddWindow
from layout_infotextwidget import InfoTextWindow
from layout_csvviewpushtoloadwidget import CSVViewPushToLoadWindow
#from layout_csvpushtoloadwidget import CSVPushToLoadWindow
from layout_resourcetrkresourcestoaddwidget import ResourcesToAddWindow

class ResourceTrkTabsWindow(QWidget):
    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.setWindowTitle("Resource Tracker")
        #self.resize(270, 110)
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "You'll create a single Resource Tracker for your study and add one entry per data or non-data/supporting file produced by or used to support the experiments/activities of your study. Through this process you'll memorialize what each data and non-data/supporting file in your study data package is/represents, how these files relate to each other, and how to drill down into these componenet data and non-data/supporting files to recreate specific published results. This will facilitate continuity and passed-down knowledge within study groups, and discovery, sharing, and re-use of the data and knowledge produced by the study outside of the original study group."
        
        
        # Create the tab widget with two tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(InfoTextWindow(self.infoText), "Info")
        self.tabs.addTab(ResourceTrkAddWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay), "Add Resource")
        self.tabs.addTab(ResourcesToAddWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay), "Check Resources To Add")
        self.tabs.addTab(CSVViewPushToLoadWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,fileBaseName="heal-csv-resource-tracker.csv",fileStartsWith="", fileTypeTitle="Resource Tracker"), "View Tracker")
        
        
                
        layout.addWidget(self.tabs)

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResourceTrkTabsWindow()
    window.show()
    sys.exit(app.exec_())



