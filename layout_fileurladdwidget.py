# https://www.youtube.com/watch?v=KVEIW2htw0A

import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMenu, QAction
from PyQt5.QtCore import Qt, QUrl, QEvent

class ListboxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        #self.resize(600,600)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self:
            print(event)
            print(source)
            self.menu = QMenu()
            
            self.rightClickDelete = QAction("Delete", self)
            self.rightClickSelect = QAction("Select", self)
            
            self.menu.addAction(self.rightClickDelete)
            #self.menu.addAction(self.rightClickSelect)
            
            if self.menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())
                print('i did it here!')
                print(item.text())
                self.takeItem(self.row(item)) 

                #self.menu.triggered[QAction].connect(self.processtrigger)
                #self.rightClickDelete.triggered.connect(lambda checked: right_click_delete())
                
            #self.menu.triggered[QAction].connect(self.processtrigger)
            #self.rightClickDelete.triggered.connect(lambda checked: right_click_delete())
                
            return True

            

        return super().eventFilter(source, event)

    def processtrigger(self,q):
      print(q.text()+" is triggered")

    def right_click_delete(self):
        print("i did it!")
        #print(bool)
        #print(q.text()+" is triggered")


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