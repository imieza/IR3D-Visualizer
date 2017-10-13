# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created: Tue Dec 13 20:54:23 2016
#      by: PyQt4 UI code generator 4.11.3
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
        MainWindow.resize(370, 371)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 370, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget_mplwidget = QtGui.QDockWidget(MainWindow)
        self.dockWidget_mplwidget.setObjectName(_fromUtf8("dockWidget_mplwidget"))
        self.dockWidgetContents_mplwidget = QtGui.QWidget()
        self.dockWidgetContents_mplwidget.setObjectName(_fromUtf8("dockWidgetContents_mplwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.dockWidgetContents_mplwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.mplwidget = MatplotlibWidget(self.dockWidgetContents_mplwidget)
        self.mplwidget.setObjectName(_fromUtf8("mplwidget"))
        self.gridLayout_2.addWidget(self.mplwidget, 0, 0, 1, 1)
        self.dockWidget_mplwidget.setWidget(self.dockWidgetContents_mplwidget)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget_mplwidget)
        self.dockWidget_Mayavi = QtGui.QDockWidget(MainWindow)
        self.dockWidget_Mayavi.setObjectName(_fromUtf8("dockWidget_Mayavi"))
        self.dockWidgetMayavi = QtGui.QWidget()
        self.dockWidgetMayavi.setObjectName(_fromUtf8("dockWidgetMayavi"))
        self.dockWidget_Mayavi.setWidget(self.dockWidgetMayavi)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget_Mayavi)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))

from matplotlibwidget import MatplotlibWidget
