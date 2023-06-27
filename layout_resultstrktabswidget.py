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
from layout_resultstrkaddwidget import ResultsTrkAddWindow
from layout_resultstrkcreatewidget import ResultsTrkCreateWindow
from layout_infotextwidget import InfoTextWindow
from layout_csvpushtoloadwidget import CSVPushToLoadWindow

class ResultsTrkTabsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Results Tracker")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "You'll create one Results Tracker for each multi-result file you share (e.g. publication, poster, etc.). Within each result tracker, add one entry per figure or text result shared in the multi-result file, and indicate the data or non-data/supporting files support/underly each result entry. <br><br>By annotating results in this way, you'll fulfill the data sharing requirements of many journals that increasingly require sharing of data that underlies published results. Memorializing this information will provide substantial utility to potential readers of your paper(s), potential secondary users of your data, potential collaborators, and to present/future members of the authoring study group that may want to revisit results in the future to replicate and/or build on their own work or the work of fellow study-group members. As such, creating results trackers will substantially contribute to facilitating continuity and passed-down knowledge within study groups, and discovery, sharing, and re-use of the data and knowledge produced by the study outside of the original study group.<br><br><b>NOTE:</b> If specific single results are used across multiple multi-result resources shared by the study group, it is still recommended that a result tracker be shared for each multi-result resource. However, specific single results that are used across multiple multi-result resources shared by the same study may easily be copied across result trackers for the distinct multi-result files."
        
        
        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(InfoTextWindow(self.infoText), "Info")
        tabs.addTab(ResultsTrkCreateWindow(), "Create Result Tracker")
        tabs.addTab(ResultsTrkAddWindow(), "Add Results")
        tabs.addTab(CSVPushToLoadWindow(), "View/Edit Tracker")
        
        
                
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
    window = ResultsTrkTabsWindow()
    window.show()
    sys.exit(app.exec_())



