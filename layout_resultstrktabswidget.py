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
from layout_csvviewpushtoloadwidget import CSVViewPushToLoadWindow
#from layout_csvpushtoloadwidget import CSVPushToLoadWindow

class ResultsTrkTabsWindow(QWidget):
    def __init__(self, workingDataPkgDirDisplay):
        super().__init__()
        self.setWindowTitle("Results Tracker")
        #self.resize(270, 110)
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "You'll create one Results Tracker for each multi-result file you share (e.g. publication, poster, etc.). Within each result tracker, add one entry per figure, table, or text result shared in the multi-result file, and indicate the data or non-data/supporting files that are required to interpret/replicate/use each result entry. <br><br> 1. For each result in your multi-result file(s), use the Annotate Result button in the Add Result tab to annotate the result <br> 2. Within the annotation of the result, indicate the multi-result file(s) in which the result is included (a single result may be shared in more than one multi-result file - e.g. a manuscript, a poster, and a presentation) <br> 3. Once you have annotated one or more results, use the Add Result to Tracker button in the Add Result tab to add one or more result annotations to the results tracker <br> 4. This will automatically create a results tracker(s), one for each multi-result file in which at least one of your annotated results is included - The automatically created Results Tracker(s) will be saved in your dsc-pkg folder. <br><br> By annotating results in this way, you'll fulfill the data sharing requirements of many journals that increasingly require sharing of data that underlies published results. Memorializing this information will provide substantial utility to potential readers of your paper(s), potential secondary users of your data, potential collaborators, and to present/future members of the authoring study group that may want to revisit results in the future to replicate and/or build on their own work or the work of fellow study-group members. As such, creating results trackers will substantially contribute to facilitating continuity and passed-down knowledge within study groups, and discovery, sharing, and re-use of the data and knowledge produced by the study outside of the original study group."
        
        
        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(InfoTextWindow(self.infoText), "Info")
        #tabs.addTab(ResultsTrkCreateWindow(), "Create Result Tracker")
        tabs.addTab(ResultsTrkAddWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay), "Add Result")
        tabs.addTab(CSVViewPushToLoadWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,fileBaseName="",fileStartsWith="heal-csv-results-tracker-", fileTypeTitle="Results Tracker"), "View Tracker")
        
        
                
        layout.addWidget(tabs)

    # def generalTabUI(self):
    #     """Create the General page UI."""
    #     generalTab = QWidget()
    #     layout = QVBoxLayout()
    #     layout.addWidget(QCheckBox("General Option 1"))
    #     layout.addWidget(QCheckBox("General Option 2"))
    #     generalTab.setLayout(layout)
    #     return generalTab

    # def networkTabUI(self):
    #     """Create the Network page UI."""
    #     networkTab = QWidget()
    #     layout = QVBoxLayout()
    #     layout.addWidget(QCheckBox("Network Option 1"))
    #     layout.addWidget(QCheckBox("Network Option 2"))
    #     networkTab.setLayout(layout)
    #     return networkTab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResultsTrkTabsWindow()
    window.show()
    sys.exit(app.exec_())



