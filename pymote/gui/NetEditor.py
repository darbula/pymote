#!/usr/bin/python

import sys
import os


from datetime import datetime
from PySide.QtGui import QMainWindow, QMenu, QCursor, QFileDialog, QMessageBox, QInputDialog
from PySide.QtCore import SIGNAL, QRect, QSize, QEvent

from IPython.lib.guisupport import get_app_qt4, start_event_loop_qt4
from NetEditorUI2 import Ui_NetEditorWindow
from graphnetwork import GNetwork
import networkx as nx
from pymote import *
from pymote.algorithms.broadcast import *
from dictionarytreemodel import DictionaryTreeModel

import numpy



class NetEditGui(QMainWindow):
    def __init__(self, net=None, fname=None):
        QMainWindow.__init__(self)

        self.network = GNetwork()


        self.ui = Ui_NetEditorWindow(self.network)
        self.ui.setupUi(self)



        #self.ui.graph.setData(pos=pos, size=1, pxMode=False)
        if net:
            self.network.network = net
            pos = self.network.getNodePositions()
            adj = self.network.getNodeAdjacency()

            self.ui.updateGraph( pos, adj, size=30, pxMode=False)

        if fname:
            #self.set_title(fname)
            pass

        self.ui._actionOpenNetwork.activated.connect(self.on_openNetwork_triggered)
        self.ui._actionAlgorithm.activated.connect(self.on_addAlgorithm_triggered)
        self.ui._actionSaveNetwork.activated.connect(self.on_saveNetwork_triggered)
        self.ui._actionRemoveNode.activated.connect(self.on_removeNode_triggered)
        self.ui._actionAddNode.activated.connect(self.on_addNode_triggered)

    def updateNetwork(self):
        self.network.network.recalculate_edges()
        self.ui.updateGraph(pos=self.network.getNodePositions(), adj=self.network.getNodeAdjacency(), size=30, pxMode=False)

    """Getters & Setters"""




    def getNetwork(self):
        pass




    """ Callbacks"""

    def on_openNetwork_triggered(self):

        default_filetype = 'gz'
        start = datetime.now().strftime('%Y%m%d') + default_filetype

        filters = ['Network pickle (*.gz)', 'All files (*)']
        selectedFilter = 'Network pickle (gz)'
        filters = ';;'.join(filters)

        fname = QFileDialog.getOpenFileName(
            self, "Choose a file to open", start, filters, selectedFilter)[0]
        if fname:
            try:
                print "open" + fname
                self.network.network = read_pickle(fname)
                pos = self.network.getNodePositions()
                adj = self.network.getNodeAdjacency()

                self.ui.graph.setData( pos=pos, adj=adj, size=30, pxMode=False)
                self.ui.graph.updateGraph()


                niModel = DictionaryTreeModel(dic=self.network.network.get_dic())
                self.ui.networkAttributeTable.setModel(niModel)
                self.ui.networkAttributeTable.expandToDepth(0)

            except Exception, e:
                print "Error opening file %s" % str(e),
                QMessageBox.critical(
                    self, "Error opening file", str(e),
                    QMessageBox.Ok, QMessageBox.NoButton)
            else:
                self.set_title(fname)

    def on_addAlgorithm_triggered(self):
        """Sets an algorithm to the network. Entry format for the input box is 'AlgorithmName,key,value'
        Example: 'Flood,informationKey,I'"""
        co = QInputDialog.getText(self, 'Set algorithm', 'Parameters:')
        cs = str(co[0]).split(",")

        name = cs[0]
        dictkey = cs[1]
        dictval = cs[2]

        exec("self.network.network.algorithms = ( (" + name + ", {'" + dictkey + "':'" + dictval + "'}), )")

    def on_removeNode_triggered(self):
        """Activates removal mode. TODO"""

        self.ui.graph.mode = "remove"
        print "remove is clicked"

    def on_saveNetwork_triggered(self):
        default_filetype = 'gz'
        start = datetime.now().strftime('%Y%m%d') + default_filetype

        filters = ['Network pickle (*.gz)', 'All files (*)']
        selectedFilter = 'Network pickle (gz)'
        filters = ';;'.join(filters)

        fname = QFileDialog.getSaveFileName(self, "Save network",
                                            start, filters, selectedFilter)[0]
        if fname:
            try:
                write_pickle(self.network.network, fname)
            except Exception, e:
                QMessageBox.critical(
                    self, "Error saving file", str(e),
                    QMessageBox.Ok, QMessageBox.NoButton)
            else:
                self.set_title(fname)

    def on_addNode_triggered(self):
        """Activates add mode"""

        if self.ui.graph.mode == "none":
            self.ui.graph.mode = "add"

        elif self.ui.graph.mode == "add":
            self.ui.graph.mode = "none"

        print "mode is" + self.ui.graph.mode





def create_window(window_class, **kwargs):
    """Create a QT window in Python, or interactively in IPython with QT GUI
    event loop integration.
    """
    global app

    app = get_app_qt4(sys.argv)
    app.references = set()

    net = None
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if os.path.exists(fname):
            net = read_pickle(fname)
        else:
            QMessageBox.critical(
                        None, "Error opening file %s", fname,
                        QMessageBox.Ok, QMessageBox.NoButton)

    window = window_class(net, fname)
    app.references.add(window)
    window.show()

    start_event_loop_qt4(app)
    return window


def main():
    global gui
    gui = create_window(NetEditGui)

if __name__ == '__main__':
    main()