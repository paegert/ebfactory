# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotwindow.ui'
#
# Created by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_plotWindow(object):
    def setupUi(self, plotWindow):
        plotWindow.setObjectName(_fromUtf8("plotWindow"))
        plotWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(plotWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.mplWidget = MatplotlibWidget(self.centralwidget)
        self.mplWidget.setGeometry(QtCore.QRect(10, 10, 781, 561))
        self.mplWidget.setObjectName(_fromUtf8("mplWidget"))
        plotWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(plotWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        plotWindow.setStatusBar(self.statusbar)

        self.retranslateUi(plotWindow)
        QtCore.QMetaObject.connectSlotsByName(plotWindow)

    def retranslateUi(self, plotWindow):
        plotWindow.setWindowTitle(_translate("plotWindow", "Plot Window", None))

from matplotlibwidget import MatplotlibWidget
