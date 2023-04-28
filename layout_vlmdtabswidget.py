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

class VLMDTabsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Dictionary")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(VLMDCreateWindow(), "Create")
        tabs.addTab(self.generalTabUI(), "View/Edit")
        tabs.addTab(self.networkTabUI(), "Validate")
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
    window = VLMDTabsWindow()
    window.show()
    sys.exit(app.exec_())



