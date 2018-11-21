# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Projekti/BMO/NetEditorUI/NetEditor2.ui'
#
# Created: Wed May 28 12:58:33 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import pyqtgraph
from NetGraphItem import NetGraphItem
import pymote
import numpy

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NetEditorWindow(object):
    def __init__(self, net):
        self.graph = NetGraphItem(net, self)
    def setupUi(self, NetEditorWindow):
        NetEditorWindow.setObjectName(_fromUtf8("NetEditorWindow"))
        NetEditorWindow.resize(873, 481)
        self._actionOpenNetwork=QtGui.QAction(NetEditorWindow)
        self.openNetwork = QtGui.QToolButton(NetEditorWindow)
        self.openNetwork.setDefaultAction(self._actionOpenNetwork)
        self.openNetwork.setGeometry(QtCore.QRect(10, 10, 31, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/fileopen.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openNetwork.setIcon(icon)
        self.openNetwork.setObjectName(_fromUtf8("openNetwork"))

        self.graphicsView = pyqtgraph.GraphicsLayoutWidget(NetEditorWindow)
        self.graphicsView.setGeometry(QtCore.QRect(15, 61, 601, 411))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))

        self.networkAttributeTable = QtGui.QTreeView(NetEditorWindow)
        self.networkAttributeTable.setGeometry(QtCore.QRect(630, 60, 231, 261))
        self.networkAttributeTable.setObjectName(_fromUtf8("tableView"))
        self.header = ['Attribute', 'Value']


        self.spinBox = QtGui.QSpinBox(NetEditorWindow)
        self.spinBox.setGeometry(QtCore.QRect(450, 20, 60, 27))
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.spinBox.setMaximum(1000)
        self.spinBox.setMinimum(10)


        self._actionAlgorithm = QtGui.QAction(NetEditorWindow)
        self.addAlgorithm = QtGui.QToolButton(NetEditorWindow)
        self.addAlgorithm.setGeometry(QtCore.QRect(520, 20, 98, 27))
        self.addAlgorithm.setObjectName(_fromUtf8("pushButton"))
        self.addAlgorithm.setDefaultAction(self._actionAlgorithm)

        self._actionSaveNetwork=QtGui.QAction(NetEditorWindow)
        self.saveNetwork = QtGui.QToolButton(NetEditorWindow)
        self.saveNetwork.setDefaultAction (self._actionSaveNetwork)
        self.saveNetwork.setGeometry(QtCore.QRect(60, 10, 31, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/3floppy_unmount.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveNetwork.setIcon(icon1)
        self.saveNetwork.setObjectName(_fromUtf8("saveNetwork"))

        self._actionRemoveNode=QtGui.QAction(NetEditorWindow)
        self.removeNode = QtGui.QToolButton(NetEditorWindow)
        self.removeNode.setDefaultAction(self._actionRemoveNode)
        self.removeNode.setGeometry(QtCore.QRect(130, 10, 41, 31))
        self.removeNode.setObjectName(_fromUtf8("closeNetwork"))

        self._actionAddNode = QtGui.QAction(NetEditorWindow)
        self.nodeAdd = QtGui.QToolButton(NetEditorWindow)
        self.nodeAdd.setGeometry(QtCore.QRect(200, 10, 41, 31))
        self.nodeAdd.setObjectName(_fromUtf8("NodeAdd"))
        self.nodeAdd.setDefaultAction(self._actionAddNode)

        self.vb = self.graphicsView.addViewBox()
        self.vb.setAspectLocked()

        self.vb.addItem(self.graph)

        self.retranslateUi(NetEditorWindow)
        QtCore.QMetaObject.connectSlotsByName(NetEditorWindow)

    def updateGraph(self, pos, adj, size, pxMode):
         self.graph.setData(pos=pos, adj=adj, size=size, pxMode=pxMode)
    def resetGraph(self):
        self.graph = pyqtgraph.GraphItem()

    # def setTableData(self, attrMatrix):
    #     self.datamodel = QtGui.QStandardItemModel(8,2)
    #     item1 = QtGui.QStandardItem()
    #     item1.setText(_fromUtf8("Algorithm"))
    #
    #
    #     #item = QtGui.QStandardItem()
    #
    #
    #     h1 = QtGui.QStandardItem(_fromUtf8("Attribute"))
    #     h2 = QtGui.QStandardItem(_fromUtf8("Value"))
    #
    #     b1 = 0
    #     for row in attrMatrix:
    #         attrItem=QtGui.QStandardItem()
    #         valItem=QtGui.QStandardItem()
    #         attrItem.setText(row[0])
    #         valItem.setText(row[1])
    #
    #         self.datamodel.setItem(b1, 0, attrItem)
    #         self.datamodel.setItem(b1, 1, valItem)
    #         b1+=1
    #
    #     self.datamodel.setHorizontalHeaderItem(0, h1)
    #     self.datamodel.setHorizontalHeaderItem(1, h2)
    #     #self.datamodel.setItem(0,0, item1)
    #     self.networkAttributeTable.setModel(self.datamodel)

    def retranslateUi(self, NetEditorWindow):
        NetEditorWindow.setWindowTitle(QtGui.QApplication.translate("NetEditorWindow", "Pymote NetEditor", None, QtGui.QApplication.UnicodeUTF8))
        self.openNetwork.setText(QtGui.QApplication.translate("NetEditorWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.addAlgorithm.setText(QtGui.QApplication.translate("NetEditorWindow", "Algorithm", None, QtGui.QApplication.UnicodeUTF8))
        self.removeNode.setText(QtGui.QApplication.translate("NetEditorWindow", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.nodeAdd.setText(QtGui.QApplication.translate("NetEditorWindow", "+", None, QtGui.QApplication.UnicodeUTF8))



import icons_rc
