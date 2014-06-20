__author__ = 'vanja'

from pymote import *
import numpy

class GNetwork():
    def __init__(self):
        self.network = Network()
        self.nodeIdDict = {}

    def getNodePositions(self):
        """returns the numpy position array to be used for NetGraphItem"""
        nodeList = self.network.nodes()
        pos = numpy.zeros((len(nodeList), 2))

        #b1=0
        for b1, ni in enumerate(nodeList):
            #self.pos([ni.network.pos[ni][0], ni.network.pos[ni][1]])
            self.nodeIdDict[ni.id] = b1
            posit = ni.network.pos[ni]

            pos[b1,0] = posit[0]
            pos[b1,1] = posit[1]
            #b1+=1
        return pos

    def getNodeAdjacency(self):
        """Returns the numpy adjacency matrix to be used for NetGraphItem"""
        adjDict = self.network.adj


        adj = numpy.zeros((len(self.network.nodes()) ** 2, 2), dtype=numpy.int)
        b1 = int()
        b1 = 0
        for ni in adjDict:
            neighbors = adjDict[ni]
            for i in neighbors:
                adj[b1,0] = self.nodeIdDict[ni.id]
                adj[b1,1] = self.nodeIdDict[i.id]
                b1+=1

        return adj

    def setNetwork(self, pos):
        b1 = 0
        for key, value in self.network.pos.items():
            self.network.pos[key] = pos[b1]
            b1+=1
        self.network.recalculate_edges()