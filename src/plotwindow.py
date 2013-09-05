'''
@package: plotwindow
@author   : map
@version  : \$Revision: 1.2 $
@Date      : \$Date: 2013/09/05 19:00:03 $

Code for the plotwindow of lcview
 
$Log: plotwindow.py,v $
Revision 1.2  2013/09/05 19:00:03  paegerm
checking for symbols to be none, adding limits and labels

checking for symbols to be none, adding limits and labels

Revision 1.1  2013/08/13 19:34:32  paegerm
Initial revision
'''

import sys
import numpy as np

from PyQt4 import QtCore, QtGui
from plotwindowui import Ui_plotWindow

from sqlitetools import dbreader as dbr

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as pl



class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)

        #self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)



    def compute_initial_figure(self):
        pass
    
    def plot_figure(self, data):
        pass



class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        u = np.cos(2 * np.pi * t)
        self.axes.plot(t, s, 'b')
        self.axes.plot(t, u, 'g')
    
    
    def plot_figure(self, data):
        for (x, y, symbol) in data:
            if symbol == None:
                self.axes.plot(x, y)
            else:
                self.axes.plot(x, y, symbol)



class PlotWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_plotWindow()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Plot window")
        
            
        self.main_widget = QtGui.QWidget(self)
        l = QtGui.QVBoxLayout(self.main_widget)
        self.pwidget = MyStaticMplCanvas(self.main_widget, width=5, height=4, 
                                         dpi=100)
        l.addWidget(self.pwidget)
        self.setCentralWidget(self.main_widget)



    def plot_figure(self, data, title, xlabel, xlim = None, 
                    ylabel = None, ylim = None, legends = None):
        self.fsize = 18
        if xlim != None:
            self.pwidget.axes.set_xlim(xlim)
        for label in self.pwidget.axes.get_xticklabels() + \
                     self.pwidget.axes.get_yticklabels():
            label.set_fontsize(self.fsize - 2)
        self.pwidget.axes.set_title(title, fontsize = self.fsize)
        self.pwidget.axes.set_xlabel(xlabel, fontsize = self.fsize)
        if ylabel != None:
            self.pwidget.axes.set_ylabel(ylabel, fontsize = self.fsize)
        self.pwidget.plot_figure(data)
        if legends != None:
            self.pwidget.axes.legend(legends, fontsize=16)
        self.pwidget.draw()
        self.main_widget.setFocus()
        # self.statusBar().showMessage("All hail matplotlib!", 2000)
        


    def closeEvent(self, ce):
        if (self.parent() != None):
            self.parent().close_child()
        self.close()
        


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = PlotWindow()
    from utilclasses import LogData
    log = LogData('/home/map/data/asas11/testcoeffs/coeffslog26_30.txt26_0')
    plotdata = [(log.idx, log.verr, None)]
    legends = ['verr']
    myapp.plot_figure(plotdata, 'myplot', 'iter', None, 'error', None, legends)
    myapp.show()
    sys.exit(app.exec_())
