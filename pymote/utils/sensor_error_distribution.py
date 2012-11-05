"""
Display sensor readings error of nodes in network given in .npc formated file.
"""
import sys, os
from pymote.npickle import read_npickle
from numpy import sqrt, arctan2, pi
from matplotlib.pyplot import hist
import pylab as P

if __name__ == '__main__':
    net = None
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if os.path.exists(fname):
            net = read_npickle(fname)
        else:
            print "Error opening file %s" % fname,
    distErr = []
    aoaErr = []
    for node in net.nodes():
        p = net.pos[node]
        o = net.ori[node]
        for neighbor,dist in node.memory['sr']['Dist'].items(): 
            trueDist = sqrt((p[0]-net.pos[neighbor][0])**2+(p[1]-net.pos[neighbor][1])**2) 
            distErr.append(dist-trueDist)
        for neighbor,aoa in node.memory['sr']['AoA'].items():
            v = net.pos[neighbor] - p
            trueAoa = (arctan2(v[1],v[0])-o)%(2*pi) 
            aoaErr.append(aoa-trueAoa)
            
    distFig = P.figure()
    ax = distFig.add_subplot(111)
    n, bins, patches = hist(distErr, 50, normed=1, histtype='stepfilled')
    y = P.normpdf( bins, 0, 10)
    l = P.plot(bins, y, 'k--', linewidth=1.5)
    
    aoaFig = P.figure()
    ax = aoaFig.add_subplot(111)
    n, bins, patches = hist(aoaErr, 50, normed=1, histtype='stepfilled')
    y = P.normpdf( bins, 0, 0.175)
    l = P.plot(bins, y, 'k--', linewidth=1.5)
    
    P.show()
