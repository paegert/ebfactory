# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lcview.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(802, 593)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.lcWidget = QtGui.QTableWidget(self.centralwidget)
        self.lcWidget.setGeometry(QtCore.QRect(5, 80, 791, 291))
        self.lcWidget.setObjectName(_fromUtf8("lcWidget"))
        self.lcWidget.setColumnCount(0)
        self.lcWidget.setRowCount(0)
        self.loadDictButton = QtGui.QPushButton(self.centralwidget)
        self.loadDictButton.setGeometry(QtCore.QRect(733, 410, 58, 25))
        self.loadDictButton.setObjectName(_fromUtf8("loadDictButton"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(12, 410, 64, 25))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.dnameEdit = QtGui.QLineEdit(self.centralwidget)
        self.dnameEdit.setGeometry(QtCore.QRect(80, 410, 649, 24))
        self.dnameEdit.setObjectName(_fromUtf8("dnameEdit"))
        self.dictWidget = QtGui.QTableWidget(self.centralwidget)
        self.dictWidget.setGeometry(QtCore.QRect(10, 440, 781, 71))
        self.dictWidget.setObjectName(_fromUtf8("dictWidget"))
        self.dictWidget.setColumnCount(0)
        self.dictWidget.setRowCount(0)
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 781, 60))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.fnameEdit = QtGui.QLineEdit(self.layoutWidget)
        self.fnameEdit.setObjectName(_fromUtf8("fnameEdit"))
        self.gridLayout.addWidget(self.fnameEdit, 0, 1, 1, 1)
        self.loadButton = QtGui.QPushButton(self.layoutWidget)
        self.loadButton.setObjectName(_fromUtf8("loadButton"))
        self.gridLayout.addWidget(self.loadButton, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cmdEdit = QtGui.QLineEdit(self.layoutWidget)
        self.cmdEdit.setObjectName(_fromUtf8("cmdEdit"))
        self.gridLayout.addWidget(self.cmdEdit, 1, 1, 1, 1)
        self.runButton = QtGui.QPushButton(self.layoutWidget)
        self.runButton.setObjectName(_fromUtf8("runButton"))
        self.gridLayout.addWidget(self.runButton, 1, 2, 1, 1)
        self.plotButton = QtGui.QPushButton(self.centralwidget)
        self.plotButton.setGeometry(QtCore.QRect(690, 520, 99, 25))
        self.plotButton.setObjectName(_fromUtf8("plotButton"))
        self.plotnewButton = QtGui.QPushButton(self.centralwidget)
        self.plotnewButton.setGeometry(QtCore.QRect(570, 520, 99, 25))
        self.plotnewButton.setObjectName(_fromUtf8("plotnewButton"))
        self.prevPutton = QtGui.QPushButton(self.centralwidget)
        self.prevPutton.setGeometry(QtCore.QRect(290, 380, 113, 27))
        self.prevPutton.setObjectName(_fromUtf8("prevPutton"))
        self.nextButton = QtGui.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(430, 380, 113, 27))
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 802, 24))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.label_3.setBuddy(self.dnameEdit)
        self.label.setBuddy(self.fnameEdit)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.loadButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.load_file)
        QtCore.QObject.connect(self.runButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.run_cmd)
        QtCore.QObject.connect(self.fnameEdit, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.loadButton.click)
        QtCore.QObject.connect(self.cmdEdit, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.runButton.click)
        QtCore.QObject.connect(self.dnameEdit, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.loadDictButton.click)
        QtCore.QObject.connect(self.loadDictButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.load_dict)
        QtCore.QObject.connect(self.lcWidget, QtCore.SIGNAL(_fromUtf8("itemSelectionChanged()")), MainWindow.change_star)
        QtCore.QObject.connect(self.plotButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.plot_lc)
        QtCore.QObject.connect(self.plotnewButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.plot_newlc)
        QtCore.QObject.connect(self.prevPutton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.prev)
        QtCore.QObject.connect(self.nextButton, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.next)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Lightcurve Viewer", None))
        self.lcWidget.setSortingEnabled(True)
        self.loadDictButton.setText(_translate("MainWindow", "Lo&ad", None))
        self.label_3.setText(_translate("MainWindow", "&Dict", None))
        self.label.setText(_translate("MainWindow", "F&ile", None))
        self.loadButton.setText(_translate("MainWindow", "&Load", None))
        self.label_2.setText(_translate("MainWindow", "Command", None))
        self.cmdEdit.setText(_translate("MainWindow", "select * from stars;", None))
        self.runButton.setText(_translate("MainWindow", "&Run", None))
        self.plotButton.setText(_translate("MainWindow", "&Plot", None))
        self.plotnewButton.setText(_translate("MainWindow", "Plot &New", None))
        self.prevPutton.setText(_translate("MainWindow", "&<", None))
        self.nextButton.setText(_translate("MainWindow", "&>", None))
        self.menuFile.setTitle(_translate("MainWindow", "&File", None))
        self.actionOpen.setText(_translate("MainWindow", "&Open", None))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.actionQuit.setText(_translate("MainWindow", "&Quit", None))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))

