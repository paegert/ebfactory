'''
@package: plotwindow
@author   : map
@version  : \$Revision: 1.3 $
@Date      : \$Date: 2013/12/05 17:21:28 $

Code for the plotwindow of lcview
 
$Log: plotwindow.py,v $
Revision 1.3  2013/12/05 17:21:28  paegerm
adding toolbar, streamlining code

adding toolbar, streamlining code

Revision 1.2  2013/09/05 19:00:03  paegerm
checking for symbols to be none, adding limits and labels

Revision 1.1  2013/08/13 19:34:32  paegerm
Initial revision
'''

import sys
#import numpy as np

from PyQt4 import QtCore, QtGui
from plotwindowui import Ui_plotWindow

from matplotlib.backends.backend_qt4agg \
     import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
     import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure




class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)

        #self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)



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

        self.pwidget = MyMplCanvas(self.main_widget, width = 5, height = 4, 
                                   dpi = 100)
        ntb = NavigationToolbar(self.pwidget, self.main_widget)
        l.addWidget(self.pwidget)
        l.addWidget(ntb)
        self.setCentralWidget(self.main_widget)
        


    def plot_figure(self, data, title, xlabel, xlim = None, 
                    ylabel = None, ylim = None, legends = None, fsize = 16):
        self.fsize = fsize
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
            self.pwidget.axes.legend(legends, fontsize = self.fsize)
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
