#!/usr/bin/python
__author__ = 'vanja'

import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from pymote import *

class NetGraphItem(pg.GraphItem):
    def __init__(self, m, u):
        self.dragPoint = None
        self.dragOffset = None
        self.textItems = []
        self.network = m
        self.ui = u
        self.mode = "none"
        pg.GraphItem.__init__(self)

    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return



        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first
            # pressed:
            pos = ev.buttonDownPos()
            print pos
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            nds = self.network.network.nodes()
            self.nid = nds[ind]
            if self.mode == "remove":
                nd = Node()
                self.network.network.add_node( pos=pos, node=nd)

                self.setData(pos=self.network.getNodePositions(), adj=self.network.getNodeAdjacency(), size = 30, PxMode=False)
                self.network.network.recalculate_edges()
                self.updateGraph()
                ev.ignore()
                return


            self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            self.network.setNetwork(self.data['pos'])
            if self.nid:
                self.network.network.recalculate_edges([self.nid])
            else:
                self.network.network.recalculate_edges()
            self.setData(pos=self.network.getNodePositions(), adj=self.network.getNodeAdjacency(), size=30, PxMode=False)

            self.updateGraph()

            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        self.updateGraph()
        ev.accept()

    def mouseClickEvent(self, ev):
        if ((ev.button() != QtCore.Qt.LeftButton) or (self.mode == "none")):
            ev.ignore()
            return
        else:
            ev.accept()

        if self.mode == "add":
            pos = ev.pos()
            self.addNode(pos)

            print "reg button"

        elif self.mode == "remove":
            p = ev.scenePos()
            pts = self.scatter.pointsAt(p)
            print p
            if len(pts) == 0:
                ev.ignore()
                print "deletion ignored"
                return
            ind = pts[0].data()[0]
            print ind
            nd = self.network.network.nodes()[ind]
            self.network.network.remove_node(nd)
            print "trying to remove node" + nd.id()
            self.network.recalculate_edges()
            self.setData(pos=self.network.getNodePositions, adj=self.network.getNodeAdjacency(), size=30, PxMode=False)
            self.updateGraph()



    def setData(self, **kwds):
        """Set data to be displayed, then call updateGraph()"""
        self.text = kwds.pop('text', [])
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)

        self.setTexts(self.text)





    def addNode(self, posit):
        """Adds a node to the graph and updates the network accordingly"""

        pos = posit
        nd = Node()
        nd.commRange = self.ui.spinBox.value()
        self.network.network.add_node( pos=pos, node=nd)

        self.setData(pos=self.network.getNodePositions(), adj=self.network.getNodeAdjacency(), size = 30, PxMode=False)
        self.network.network.recalculate_edges()
        self.updateGraph()

    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        
        for i,item in enumerate(self.textItems):
            item.setPos(*self.data['pos'][i])


