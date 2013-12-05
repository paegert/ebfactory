# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qplotloggui.ui'
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

class Ui_mainDialog(object):
    def setupUi(self, mainDialog):
        mainDialog.setObjectName(_fromUtf8("mainDialog"))
        mainDialog.resize(682, 468)
        self.buttonBox = QtGui.QDialogButtonBox(mainDialog)
        self.buttonBox.setGeometry(QtCore.QRect(440, 420, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.filelistWidget = DDListWidget(mainDialog)
        self.filelistWidget.setGeometry(QtCore.QRect(20, 20, 591, 371))
        self.filelistWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.filelistWidget.setObjectName(_fromUtf8("filelistWidget"))
        self.plotButton = QtGui.QPushButton(mainDialog)
        self.plotButton.setGeometry(QtCore.QRect(20, 420, 99, 25))
        self.plotButton.setObjectName(_fromUtf8("plotButton"))
        self.clearButton = QtGui.QPushButton(mainDialog)
        self.clearButton.setGeometry(QtCore.QRect(140, 420, 99, 25))
        self.clearButton.setObjectName(_fromUtf8("clearButton"))
        self.deleteButton = QtGui.QPushButton(mainDialog)
        self.deleteButton.setGeometry(QtCore.QRect(250, 420, 99, 25))
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.upButton = QtGui.QPushButton(mainDialog)
        self.upButton.setGeometry(QtCore.QRect(620, 190, 51, 25))
        self.upButton.setObjectName(_fromUtf8("upButton"))
        self.downButton = QtGui.QPushButton(mainDialog)
        self.downButton.setGeometry(QtCore.QRect(620, 220, 51, 25))
        self.downButton.setObjectName(_fromUtf8("downButton"))

        self.retranslateUi(mainDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), mainDialog.plot)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), mainDialog.reject)
        QtCore.QObject.connect(self.plotButton, QtCore.SIGNAL(_fromUtf8("clicked()")), mainDialog.plot)
        QtCore.QObject.connect(self.clearButton, QtCore.SIGNAL(_fromUtf8("clicked()")), mainDialog.clearList)
        QtCore.QObject.connect(self.deleteButton, QtCore.SIGNAL(_fromUtf8("clicked()")), mainDialog.deleteSelected)
        QtCore.QObject.connect(self.upButton, QtCore.SIGNAL(_fromUtf8("clicked()")), mainDialog.moveUp)
        QtCore.QObject.connect(self.downButton, QtCore.SIGNAL(_fromUtf8("clicked()")), mainDialog.moveDown)
        QtCore.QMetaObject.connectSlotsByName(mainDialog)

    def retranslateUi(self, mainDialog):
        mainDialog.setWindowTitle(_translate("mainDialog", "PlotLog", None))
        self.plotButton.setText(_translate("mainDialog", "&Plot", None))
        self.clearButton.setText(_translate("mainDialog", "&Clear", None))
        self.deleteButton.setText(_translate("mainDialog", "&Delete", None))
        self.upButton.setText(_translate("mainDialog", "&Up", None))
        self.downButton.setText(_translate("mainDialog", "Do&wn", None))

from qutilclasses import DDListWidget
