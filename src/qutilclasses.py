'''

@package: qutilclasses
@author   : map
@version  : \$Revision: 1.1 $
@Date      : \$Date: 2013/12/05 18:10:47 $


Helper classes for pyqt programs

DDListWidget - ListWidget allowing drag and drop
DDLineEdit - LineEdit allowing drag and drop


$Log: qutilclasses.py,v $
Revision 1.1  2013/12/05 18:10:47  paegerm
initial revision

Initial revision
'''




import sys

from PyQt4 import QtCore, QtGui



class DDListWidget(QtGui.QListWidget):
    '''
    Adding Drag and Drop
    '''
    
    postDrop = QtCore.pyqtSignal()


    def __init__(self, parent = None):
        '''
        Constructor
        '''
        QtGui.QListWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        
        
        
    def iterItems(self):
        for i in xrange(self.count()):
            yield self.item(i)
        
        
        
    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        
        
        
    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        
        
        
    def dropEvent(self, event):
        event.accept()
        if event.mimeData().hasUrls() == True:
            urls = event.mimeData().urls()
            for url in urls:
                self.addItem(url.toLocalFile())
            self.postDrop.emit()



class DDLineEdit(QtGui.QLineEdit):
    '''
    Adding Drag and Drop
    '''
    
    postDrop = QtCore.pyqtSignal()

    
    def __init__(self, parent = None):
        '''
        Constructor
        '''
        QtGui.QLineEdit.__init__(self, parent)
        self.setAcceptDrops(True)

        
        
    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        
        
        
    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        
        
        
    def dropEvent(self, event):
        event.accept()
        if event.mimeData().hasUrls() == True:
            urls = event.mimeData().urls()
            self.setText(urls[0].toLocalFile())
            self.postDrop.emit()
        elif event.mimeData().hasText() == True:
            txt = event.mimeData().text()
            self.setText(txt)
            self.postDrop.emit()
        
        
        
if __name__ == '__main__':
    pass
