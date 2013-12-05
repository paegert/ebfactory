#!/usr/bin/env python
'''
@package: qplotlog
@author   : map
@version  : \$Revision: 1.1 $
@Date      : \$Date: 2013/12/05 18:07:17 $

Takes logs written by trainnetmp -d 1 and plots the validation errors

$Log: qplotlog.py,v $
Revision 1.1  2013/12/05 18:07:17  paegerm
initial revision

Initial revision
'''

import sys
import numpy as np
import matplotlib.pyplot as pl

from PyQt4 import QtCore, QtGui
from qplotloggui import Ui_mainDialog

from utilclasses import LogData
from plotwindow import *



class MainDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_mainDialog()
        self.ui.setupUi(self)
        self.child = None
        self.logs = None
        self.legends = None
        self.plotlogs = None
        self.title = None
        self.xlabel = None
        self.ylabel = None



    def prepare(self):
        self.logs = []
        for item in self.ui.filelistWidget.iterItems():
            self.logs.append(LogData(item.text()))
        
        self.plotlogs = []
        self.legends  = []
        for i, log in enumerate(self.logs):
            self.legends.append(str(i + 1))
            self.plotlogs.append((log.idx, log.verr, None))
        self.title   = 'Validation error per exemplar in %'
        self.xlabel  = 'Iteration' 
        self.ylabel = '% error / exemplar'


        
    def plot(self):
        self.prepare()
         
        if self.child == None:
            self.child = PlotWindow(self)
        else:
            self.child.pwidget.axes.clear()
        self.child.plot_figure(self.plotlogs, self.title, self.xlabel, 
                               None, self.ylabel, None, self.legends)
        self.child.show()
                 
        
        
    def moveUp(self):
        item = self.ui.filelistWidget.currentItem()
        row = self.ui.filelistWidget.row(item)
        if row == 0:
            return
        self.ui.filelistWidget.takeItem(row)
        self.ui.filelistWidget.insertItem(row - 1, item)
        self.ui.filelistWidget.setCurrentRow(row - 1)
        
        
        
    def moveDown(self):
        item = self.ui.filelistWidget.currentItem()
        row = self.ui.filelistWidget.row(item)
        if row == self.ui.filelistWidget.count() - 1:
            return
        self.ui.filelistWidget.takeItem(row)
        self.ui.filelistWidget.insertItem(row + 1, item)
        self.ui.filelistWidget.setCurrentRow(row + 1)
        
    
        
        
    def deleteSelected(self):
        for item in self.ui.filelistWidget.selectedItems():
            self.ui.filelistWidget.takeItem(self.ui.filelistWidget.row(item))
        
        
    def clearList(self):
        self.ui.filelistWidget.clear()



    def close_child(self):
        self.child = None
        
        
        
    def closeEvent(self, ce):
        self.close()

    
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = MainDialog()
    myapp.show()
    sys.exit(app.exec_())
