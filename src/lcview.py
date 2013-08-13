'''
@package: dicttest
@author   : map
@version  : \$Revision: 1.1 $
@Date      : \$Date: 2013/08/13 19:25:53 $

Viewer for classified lightcurves

$Log: lcview.py,v $
Revision 1.1  2013/08/13 19:25:53  paegerm
initial revision

Initial revision
'''

import sys

from optparse import OptionParser

from PyQt4 import QtCore, QtGui
from lcviewui import Ui_MainWindow

from sqlitetools import dbreader as dbr
import dbconfig

from plotwindow import *



options = None

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # connect the menu actions
        QtCore.QObject.connect(self.ui.actionOpen, QtCore.SIGNAL('triggered()'),
                               self.select_file)
        QtCore.QObject.connect(self.ui.actionQuit, QtCore.SIGNAL('triggered()'),
                               QtGui.qApp, QtCore.SLOT('quit()'))
        
        # make tableWidgets read only
        self.ui.lcWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ui.lcWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        self.child = None
        
        self.offset = 0
        self.db = None
        if options.clsname != None:
            self.ui.fnameEdit.setText(options.rootdir + options.clsname)
            self.load_file()
            self.run_cmd()

        self.dictdb  = None
        self.vardb   = None
        self.star    = None
        self.staruid = 0
        self.cls1 = None
        self.prob1 = None
        if options.dictname != None:
            self.ui.dnameEdit.setText(options.rootdir + options.dictname)
            self.load_dict()
            
        self.plcdb = None
        if options.plcname != None:
            self.plcdb = dbr.DbReader(options.rootdir + options.plcname)
            
        self.blcdb = None
        if options.blcname != None:
            self.blcdb = dbr.DbReader(options.rootdir + options.blcname)
        
        self.fitdb = None
        if options.fitname != None:
            self.fitdb = dbr.DbReader(options.rootdir + options.fitname)



    def select_file(self):
        infile = QtGui.QFileDialog.getOpenFileName()
        if infile:
            self.ui.fnameEdit.setText(infile)
            self.load_file()
        


    def load_file(self):
        fname = str(self.ui.fnameEdit.text())
        self.db = dbr.DbReader(fname)
        res = self.db.fetchall("SELECT * FROM sqlite_master WHERE type='table';")
        # print res[0].keys()
        self.tname = res[0][1]
        self.ui.cmdEdit.setText('select * from ' + self.tname + ' order by prob1 desc')
        


    def load_dict(self):
        dname = str(self.ui.dnameEdit.text())
        self.dictdb = dbr.DbReader(dname)
        
        
        
    def run_cmd(self):
        self.ui.lcWidget.clear()
        self.ui.lcWidget.setRowCount(0)
        cmd = str(self.ui.cmdEdit.text()) + ' limit 100 offset ' + \
              str(self.offset)
        self.rows = self.db.fetchmany(cmd, None, 100)
        for i, row in enumerate(self.rows):
            if (i == 0):
                self.cols = row.keys()
                self.ui.lcWidget.setColumnCount(len(self.cols))
                self.ui.lcWidget.setHorizontalHeaderLabels(self.cols)
            self.ui.lcWidget.insertRow(i)
            for j, col in enumerate(row):
                item = QtGui.QTableWidgetItem(str(col));
                self.ui.lcWidget.setItem(i, j, item)
        
        
        
    def change_star(self):
        row  = self.ui.lcWidget.currentRow()
        cell = self.ui.lcWidget.item(row, 1)
        self.staruid = int(cell.text())
        cell = self.ui.lcWidget.item(row, 4)
        self.cls1 = cell.text()
        cell = self.ui.lcWidget.item(row, 5)
        self.prob1 = str(round(float(cell.text()), 4))
        if self.dictdb != None:
            cmd  = 'select * from stars where uid = ?'
            self.star = self.dictdb.fetchone(cmd, (self.staruid,))
            cols = self.star.keys()
            self.ui.dictWidget.setColumnCount(len(cols))
            self.ui.dictWidget.setHorizontalHeaderLabels(cols)
            self.ui.dictWidget.setRowCount(1)
            for i, col in enumerate(self.star):
                item = QtGui.QTableWidgetItem(str(col))
                self.ui.dictWidget.setItem(0, i, item)
            
    
    
    def plot_lc(self):
        if self.staruid == 0:
            QtGui.QMessageBox.critical(self, 'Error', 'No star Selected')
            return
        
        plcphases = None
        plcmags   = None
        if self.plcdb != None:
            res = self.plcdb.getlc(self.staruid)
            plcphases = [x[3] for x in res]
            plcmags   = [x[4] for x in res]

        blcphases = None
        blcmags   = None
        if self.blcdb != None:
            res = self.blcdb.getlc(self.staruid)
            blcphases = [x[2] for x in res]
            blcmags   = [x[3] for x in res]
    
        midphases  = None
        midvalues  = None
        fitphases = None
        fitvalues = None
        if self.fitdb != None:
            mid = self.fitdb.getlc(self.staruid, tname = 'midpoints')
            if mid != None and len(mid) > 0:
                midphases = []
                midvalues = []
                for i in range(4):
                    midphases.append(mid[0][4 * i + 2])    # knot
                    midvalues.append(mid[0][4 * i + 3])    # flux of knot
                    midphases.append(mid[0][4 * i + 4])    # midpoint
                    midvalues.append(mid[0][4 * i + 5])    # flux of midpoint
                
            fit = self.fitdb.getlc(self.staruid, tname = 'fit')
            if fit != None and len(fit) > 0:
                fitphases = [x[2] for x in fit]
                fitvalues = [x[3] for x in fit]
            else:
                coeffs = self.fitdb.getlc(self.staruid, 'coeffs')
                fitphases = np.linspace(-0.5, 0.5, 100)
                fitvalues = []
                for x in fitphases:
                    if x >= coeffs[0]['knot1'] and x < coeffs[0]['knot2']:
                        xx = x - coeffs[0]['knot1']
                        y = coeffs[0]['c11'] + coeffs[0]['c12'] * xx + \
                            coeffs[0]['c13'] * xx * xx
                        fitvalues.append(y)
                    elif x >= coeffs[0]['knot2'] and x < coeffs[0]['knot3']:
                        xx = x - coeffs[0]['knot2']
                        y = coeffs[0]['c21'] + coeffs[0]['c22'] * xx + \
                            coeffs[0]['c23'] * xx * xx
                        fitvalues.append(y)
                    elif x >= coeffs[0]['knot3'] and x < coeffs[0]['knot4']:
                        xx = x - coeffs[0]['knot3']
                        y = coeffs[0]['c31'] + coeffs[0]['c32'] * xx + \
                            coeffs[0]['c33'] * xx * xx
                        fitvalues.append(y)
                    elif x >= coeffs[0]['knot4'] or x < coeffs[0]['knot1']:
                        dknot = 1.0 + coeffs[0]['knot1'] - coeffs[0]['knot4']
                        if x < coeffs[0]['knot1']:
                            knot = coeffs[0]['knot4'] - 1
                        else:
                            knot = coeffs[0]['knot4']
                        xx = x - knot
                        y = coeffs[0]['c41'] + coeffs[0]['c42'] * xx + \
                            coeffs[0]['c43'] * xx * xx
                        # correct for wrapping around
                        y -= coeffs[0]['c43'] * xx * dknot
                        fitvalues.append(y)

        plotlcs = [(plcphases, plcmags, 'k.'), (blcphases, blcmags, 'r.'), 
                   (fitphases, fitvalues, 'b-'), (midphases, midvalues, 'go')]
        title   = self.star['id'] + '  ' + self.star['varcls'] + '  (' + \
                  self.cls1 + ': ' + self.prob1 + ')'
        xlabel  = 'Phase (Period = ' + str(self.star['period']) + 'd)' 
        
        if self.child == None:
            self.child = PlotWindow(self)
        else:
            self.child.pwidget.axes.clear()
        self.child.plot_figure(plotlcs, title, xlabel)
        self.child.show()
        
        
    def close_child(self):
        self.child = None
        
        
    
    def closeEvent(self, ce):
        if self.db != None:
            self.db.close()
        if self.dictdb != None:
            self.dictdb.close()
        if self.plcdb != None:
            self.plcdb.close()
        if self.blcdb != None:
            self.blcdb.close()
        if self.fitdb != None:
            self.fitdb.close()
        self.close()
        


if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--cls', dest='clsname', type='string', 
                      default='asascls.sqlite',
                      help='classification database')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file (asasdict.sqlite)')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='asasfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fittype', dest='fittype', type='string', 
                      default='coeffs',
                      help='coeffs (default) / midpoints')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='asasnplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--polydir', dest='polydir', type='string', 
                      default=None,
                      help='directory for polyfit files (default = None)')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./')
    parser.add_option('--var', dest='varname', type='string', 
                      default=None,
                      help='database file with variable star parameters')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()

    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
    