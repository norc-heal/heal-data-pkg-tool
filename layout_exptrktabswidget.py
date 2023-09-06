#https://realpython.com/python-pyqt-layout/#:~:text=addTab()%20%2C%20then%20that%20icon,layout%20containing%20the%20required%20widgets.

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from layout_vlmdcreatewidget import VLMDCreateWindow
from layout_exptrkaddwidget import ExpTrkAddWindow
from layout_csvviewpushtoloadwidget import CSVViewPushToLoadWindow
#from layout_csvpushtoloadwidget import CSVPushToLoadWindow
from layout_infotextwidget import InfoTextWindow

class ExpTrkTabsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Experiment Tracker")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "You'll create a single experiment tracker for your study and add one entry per component experiment that is part of your study. Many clinical studies may have a single experiment to list, whereas many pre-clinical/basic science studies use several component experiments to address study aims, and should list each of those experiments in the Experiment Tracker. This will provide a clear overview of what experiments/activities were undertaken as part of your study, why (what questions you hoped to address with these experiments/activities), and what you thought might be the results of these experiments/activities. This allows you to memorialize what each experiment/activity undertaken by your study is/represents, and how it was approached by your study group. This will facilitate continuity and passed-down knowledge within study groups, and sharing and re-use of the data and knowledge produced by your study outside of the original study group."
        
        
        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(InfoTextWindow(self.infoText), "Info")
        tabs.addTab(ExpTrkAddWindow(), "Add Experiment")
        tabs.addTab(CSVViewPushToLoadWindow(), "View Tracker")
        
                
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
    window = ExpTrkTabsWindow()
    window.show()
    sys.exit(app.exec_())



