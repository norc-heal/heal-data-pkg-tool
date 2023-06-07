# https://www.youtube.com/watch?v=KVEIW2htw0A

import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QUrl

class ListboxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        #self.resize(600,600)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else: 
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []

            print(event.mimeData().urls())

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))

            self.addItems(links)
            self.links = links
        else:
            event.ignore()



class AppDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200,600)

        self.lstbox_view = ListboxWidget(self)

        self.btn = QPushButton("Get Value",self)
        self.btn.setGeometry(850, 400, 200, 50)

        #self.btn.clicked.connect(self.getSelectedItem)
        self.btn.clicked.connect(self.getList)

    def getSelectedItem(self):
        item = QListWidgetItem(self.lstbox_view.currentItem())
        print(item.text())

    def getList(self):
        #item = QListWidgetItem(self.lstbox_view.currentItem())
        #print(item.text())
        lw = self.lstbox_view

        items = [lw.item(x).text() for x in range(lw.count())]
        print(items)



#app = QApplication(sys.argv)
#demo = AppDemo()
#demo.show()
#sys.exit(app.exec_())

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateResourceWindow()
    window.show()
    sys.exit(app.exec_())