import sys, os, numpy
from PyQt4 import QtGui
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from pymote import * #@UnusedWildImport
from networkx.drawing.nx_pylab import draw_networkx_edges
from datetime import datetime
from matplotlib.collections import PatchCollection, Collection
import networkx as nx
from pymote.nodealgorithm import NodeAlgorithm
   
class SimulationGui(QtGui.QMainWindow):
    def __init__(self, net=None, parent=None, fname=None):
        QtGui.QMainWindow.__init__(self)
        
        self.ui = Ui_SimulationWindow()
        self.ui.setupUi(self)
        
        if fname: self.set_title(fname)
        
        # context menu
        self.ui.nodeInspector.addAction(self.ui.actionCopyInspectorData)
        self.ui.nodeInspector.addAction(self.ui.actionShowLocalizedSubclusters)
        
        self.dpi = 72
        # take size of networDisplayWidget
        self.fig = Figure((700/self.dpi,731/self.dpi),self.dpi,facecolor='0.9')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.networkDisplayWidget)
        self.nav = NavigationToolbar(self.canvas, self.ui.networkDisplayWidget, coordinates=True)
        self.nav.setGeometry(QtCore.QRect(0, 0, 651, 36))
        self.nav.setIconSize(QtCore.QSize(24, 24))
        
        self.axes = self.fig.add_subplot(111)
        #http://matplotlib.sourceforge.net/api/figure_api.html#matplotlib.figure.SubplotParams
        self.fig.subplots_adjust(left=0.03,right=0.99,top=0.92)
        
        if net:
            self.init_sim(net)
        
        self.connect(self.ui.showNodes,QtCore.SIGNAL('stateChanged(int)'),self.refresh_visibility)
        self.connect(self.ui.showEdges,QtCore.SIGNAL('stateChanged(int)'),self.refresh_visibility)
        self.connect(self.ui.showMessages,QtCore.SIGNAL('stateChanged(int)'),self.refresh_visibility)
        self.connect(self.ui.showLabels,QtCore.SIGNAL('stateChanged(int)'),self.refresh_visibility)
        self.connect(self.ui.redrawNetworkButton,QtCore.SIGNAL('clicked(bool)'),self.redraw)
        self.connect(self.ui.treeGroupBox,QtCore.SIGNAL('toggled(bool)'),self.refresh_visibility)
        self.connect(self.ui.treeKey,QtCore.SIGNAL('textEdited(QString)'),self.redraw)
        self.connect(self.ui.propagationError,QtCore.SIGNAL('toggled(bool)'),self.refresh_visibility)
        self.connect(self.ui.locKey,QtCore.SIGNAL('textEdited(QString)'),self.redraw)

        # http://matplotlib.sourceforge.net/api/backend_bases_api.html#matplotlib.backend_bases.FigureCanvasBase.mpl_connect
        self.canvas.mpl_connect('pick_event', self.on_pick)
    
    
    def init_sim(self, net):
        self.net = net
        self.sim = Simulation(net)
        self.connect(self.sim,QtCore.SIGNAL("redraw()"),self.redraw)
        self.connect(self.sim,QtCore.SIGNAL("updateLog(QString)"),self.update_log)
        self.redraw()
        
        
    def update_log(self, text):
        """ Add item to list widget """
        print "Add: " + text
        self.ui.logListWidget.insertItem(0,text)
        #self.ui.logListWidget.sortItems()
    
    def redraw(self):
        self.refresh_network_inspector()
        self.draw_network()
        self.reset_zoom()
    
    def draw_network(self, net=None, clear=True, subclusters=None, drawMessages=True):
        if not net: net = self.net
        currentAlgorithm = self.net.algorithms[self.net.algorithmState['index']]
        if clear: self.axes.clear()
        self.axes.imshow(self.net.environment.im,vmin=0,cmap='binary_r')
        
        self.draw_tree(str(self.ui.treeKey.text()),net)
        self.draw_edges(net)
        self.draw_propagation_errors(str(self.ui.locKey.text()),net)
        if subclusters:
            node_colors = self.get_node_colors(net,subclusters=subclusters)
        else:
            node_colors = self.get_node_colors(net,algorithm=currentAlgorithm)
        self.node_collection = self.draw_nodes(net,node_colors)
        if drawMessages:
            self.draw_messages(net)
        self.draw_labels(net)
        self.drawnNet = net
        step_text = ' (step %d)' % self.net.algorithmState['step'] if isinstance(currentAlgorithm,NodeAlgorithm) else ''
        self.axes.set_title(currentAlgorithm.name+step_text)
        
        self.refresh_visibility()
        
    def draw_nodes(self,net=None,node_colors={},node_radius={}):
        if not net: net = self.net
        if type(node_colors)==str:
            node_colors = {node:node_colors for node in net.nodes()}
        nodeCircles = []
        for n in net.nodes():
            c = NodeCircle(tuple(net.pos[n]), node_radius.get(n,8.0), color=node_colors.get(n,'r'), 
                       ec='k', lw=1.0, ls='solid',picker=3)
            nodeCircles.append(c)
        node_collection = PatchCollection(nodeCircles,match_original=True)
        node_collection.set_picker(3)
        self.axes.add_collection(node_collection)
        return node_collection       

    def get_node_colors(self,net,algorithm=None,subclusters=None,drawLegend=True):
            COLORS = 'rgbcmyw'*100
            node_colors = {}
            if algorithm:
                color_map = {}
                if isinstance(algorithm,NodeAlgorithm):
                    for ind,status in enumerate(algorithm.STATUS.keys()):
                        if status == 'IDLE':
                            color_map.update({status:'k'})
                        else:
                            color_map.update({status:COLORS[ind]})
                    if drawLegend:
                        proxy = []
                        labels = []
                        for status,color in color_map.items():
                            proxy.append(Circle((0, 0), radius=8.0, color=color, ec='k', 
                                                lw=1.0, ls='solid'))
                            labels.append(status)
                        self.fig.legends = []
                        self.fig.legend(proxy,labels,loc=8,prop={'size':'10.0'},ncol=len(proxy),
                                        title='Statuses for %s:' % algorithm.name)
                for n in net.nodes():
                    if n.status == '' or not n.status in color_map.keys():
                        node_colors[n] = 'r'
                    else:
                        node_colors[n] = color_map[n.status]
            elif subclusters:
                for i,sc in enumerate(subclusters):
                    for n in sc:
                        if node_colors.has_key(n):
                            node_colors[n] = 'k'
                        else:
                            node_colors[n] = COLORS[i]
            return node_colors
                    
    def draw_edges(self,net=None):
        if not net: net = self.net
        self.edge_collection = nx.draw_networkx_edges(net,net.pos,alpha=0.6,edgelist=None,ax=self.axes)
    
    def draw_messages(self,net=None):
        if not net: net = self.net
        self.messages = []
        msgCircles = []
        for node in net.nodes():
            for msg in node.outbox:
                #broadcast
                if msg.destination is None:
                    for neighbor in net.adj[node].keys():
                        nbr_msg = msg.copy()
                        nbr_msg.destination = neighbor
                        c = MessageCircle(nbr_msg,net,'out',3.0,lw=0,picker=3,zorder=3,color='b')
                        self.messages.append(nbr_msg)
                        msgCircles.append(c)
                else:        
                    c = MessageCircle(msg,net,'out',3.0,lw=0,picker=3,zorder=3,color='b')
                    self.messages.append(msg)
                    msgCircles.append(c)
            for msg in node.inbox:
                c = MessageCircle(msg,net,'in',3.0,lw=0,picker=3,zorder=3,color='r')
                self.messages.append(msg)
                msgCircles.append(c)
        if self.messages:
            self.message_collection = PatchCollection(msgCircles,match_original=True)
            self.message_collection.set_picker(3)
            self.axes.add_collection(self.message_collection)

    def draw_labels(self, net=None): 
        if not net: 
            net = self.net  
        label_pos = {}
        for n in net.nodes():
            label_pos[n] = net.pos[n].copy() + 10
        self.label_collection = nx.draw_networkx_labels(net,label_pos,labels=net.labels,ax=self.axes)

    
    def refresh_visibility(self):
        try:
            self.node_collection.set_visible(self.ui.showNodes.isChecked())
            self.edge_collection.set_visible(self.ui.showEdges.isChecked())
            for label in self.label_collection.values():
                label.set_visible(self.ui.showLabels.isChecked())
            self.tree_collection.set_visible(self.ui.treeGroupBox.isChecked())
            self.ini_error_collection.set_visible(self.ui.propagationError.isChecked())
            self.propagation_error_collection.set_visible(self.ui.propagationError.isChecked())
            # sould be last, sometimes there are no messages
            self.message_collection.set_visible(self.ui.showMessages.isChecked())
        except AttributeError:
            print 'Refresh visibility warning'
        self.canvas.draw()
        
    def draw_tree(self, treeKey, net=None):
        """ 
        Show tree representation of network.     
        
        treeKey -- key in nodes memory (dictionary) where parent and 
                   children data is stored in format:
                    {'parent': parent_node,
                     'children': [child_node1, child_node2 ...]}
        """
        if not net: net = self.net
        treeNet = net.get_tree_net(treeKey)
        if treeNet:
            self.tree_collection = draw_networkx_edges(treeNet,treeNet.pos,treeNet.edges(),width=1.8,alpha=0.6,ax=self.axes)
    
    def draw_propagation_errors(self,locKey,net):
        SCALE_FACTOR = 0.6
        if not net: net = self.net
        if any([not node.memory.has_key(locKey) for node in net.nodes()]): 
            self.propagation_error_collection = []
            self.ini_error_collection = []
            return
            
        rms = {'iniRms': {},'stitchRms': {}}
        for node in net.nodes():
            rms['iniRms'][node] = get_rms(self.net.pos,(node.memory['iniLocs']),True)*SCALE_FACTOR
            rms['stitchRms'][node] = get_rms(self.net.pos,node.memory[locKey],True)*SCALE_FACTOR
        self.propagation_error_collection = self.draw_nodes(net=net,node_colors='g',node_radius=rms['stitchRms'])
        self.ini_error_collection = self.draw_nodes(net=net,node_colors='b',node_radius=rms['iniRms'])
            
    def reset_zoom(self):
        self.axes.set_xlim((0, self.net.environment.im.shape[1]))
        self.axes.set_ylim((0, self.net.environment.im.shape[0]))
        
    def set_title(self,fname):
        self.setWindowTitle(' - '.join([str(self.windowTitle()).split(' - ')[0],str(fname)]))

    def refresh_network_inspector(self):
        niModel = DictionaryTreeModel(dic=self.net.get_dic())
        self.ui.networkInspector.setModel(niModel)
        self.ui.networkInspector.expandToDepth(0)
    
    """
    Callbacks
    """
    
    def on_actionRun_triggered(self,checked=None):
        if checked is None: return
        self.ui.logListWidget.clear()        
        print 'running ...',     
        self.sim.stepping = True
        self.sim.run_all()

    def on_actionStep_triggered(self,checked=None):
        if checked is None: return
        print 'next step ...',
        self.sim.run(self.ui.stepSize.value())      

    def on_actionReset_triggered(self,checked=None):
        if checked is None: return
        print 'reset ...',
        self.sim.reset()
        self.redraw()    

    def on_actionCopyInspectorData_triggered(self,checked=None):
        if checked is None: return
        str = 'Node inspector data\n-------------------'
        #raise()
        for qModelIndex in self.ui.nodeInspector.selectedIndexes():
            str += '\n'+qModelIndex.internalPointer().toString('    ')
            
        clipboard = app.clipboard()
        clipboard.setText(str)
        event = QtCore.QEvent(QtCore.QEvent.Clipboard)
        app.sendEvent(clipboard, event)
        
    def on_actionShowLocalizedSubclusters_triggered(self,checked=None):
        if checked is None: return
        if len(self.ui.nodeInspector.selectedIndexes())==1:
            qModelIndex = self.ui.nodeInspector.selectedIndexes()[0]
            treeItem = qModelIndex.internalPointer()
            assert(isinstance(treeItem.itemDataValue,dict))
            
            estimated = deepcopy(treeItem.itemDataValue)
            # rotate, translate and optionally scale 
            # w.r.t. original positions (pos)
            align_clusters([self.net.pos],[estimated], False)
            net = self.net.subgraph(estimated.keys(),pos=estimated)
            
            self.draw_network(net=net,drawMessages=False)

            edge_pos = numpy.asarray([(self.net.pos[node],estimated[node][:2]) for node in net])
            error_collection = LineCollection(edge_pos,colors='r')
            self.axes.add_collection(error_collection)
            
            rms = get_rms(self.net.pos, [estimated], scale=False)
            self.update_log('rms = %.3f' % rms)
            self.update_log('localized = %.2f%% (%d/%d)' % 
                            (len(estimated)*1./len(self.net.pos)*100,
                            len(estimated),len(self.net.pos)))
        
    def on_actionSaveNetwork_triggered(self, checked=None, *args):
        if checked is None: return
        default_filetype = 'gz'
        start = datetime.now().strftime('%Y%m%d') + default_filetype
        
        filters = ['Network pickle (*.gz)','All files (*)']
        selectedFilter = 'Network pickle (gz)'
        filters = ';;'.join(filters)

        fname = QtGui.QFileDialog.getSaveFileName(
            self, "Choose a filename to save to", start, filters, selectedFilter)
        if fname:
            try:
                write_npickle(self.net, fname) 
            except Exception, e:
                QtGui.QMessageBox.critical(
                    self, "Error saving file", str(e),
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            else:
                self.set_title(fname)
    
    def on_actionOpenNetwork_triggered(self, checked=None, *args):
        if checked is None: return
        default_filetype = 'gz'
        start = datetime.now().strftime('%Y%m%d') + default_filetype
        
        filters = ['Network pickle (*.gz)','All files (*)']
        selectedFilter = 'Network pickle (gz)'
        filters = ';;'.join(filters)

        fname = QtGui.QFileDialog.getOpenFileName(
            self, "Choose a file to open", start, filters, selectedFilter)
        if fname:
            try:
                net = read_npickle(fname)
                self.init_sim(net)
            except Exception, e:
                print "Error opening file %s" % str(e),
                QtGui.QMessageBox.critical(
                    self, "Error opening file", str(e),
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            else:
                self.set_title(fname)
                
    def on_pick(self,event):
        if event.artist==self.node_collection or event.artist==self.propagation_error_collection or event.artist==self.ini_error_collection:
            for ind in event.ind:
                self.on_pick_node(self.drawnNet.nodes()[ind])
        elif event.artist==self.message_collection:
            for ind in event.ind:
                self.on_pick_message(self.messages[ind])
        self.canvas.draw()

    def on_pick_node(self,node):
        niModel = DictionaryTreeModel(dic=node.get_dic())
        #TODO: self.ui.nodeInspectorLabel.setText('Node inspector (node %d)' % node.id)
        self.ui.nodeInspector.setModel(niModel)
        self.ui.nodeInspector.expandToDepth(0)

    def on_pick_message(self,message):
        self.ui.logListWidget.insertItem(0, 'Pick message %s ' % repr(message))

class NodeCircle(Circle):
    """ Circle with node data. """
    def __init__(self,xy,*args,**kwargs):
        Circle.__init__(self,xy,*args,**kwargs)

class MessageCircle(Circle):
    """ Circle with message data. """
    def __init__(self,message,net,direction,*args,**kwargs):
        Circle.__init__(self,self._get_pos(message,net,direction),*args,**kwargs)
    
    def _get_pos(self,message,net,direction):
        xd,yd = net.pos[message.destination]
        try: xs,ys = net.pos[message.source]
        except KeyError: return (xd,yd)
        x=(xs+xd)/2.0       # middle point
        y=(ys+yd)/2.0
        if direction=='out':
            x=(xs+x)/2.0        # one quarter from source
            y=(ys+y)/2.0
            x=(xs+x)/2.0        # one eighth from source
            y=(ys+y)/2.0
        elif direction=='in':
            x=(xd+x)/2.0        # one quarter from destination
            y=(yd+y)/2.0
            x=(xd+x)/2.0        # one eighth from destination
            y=(yd+y)/2.0
            x=(xd+x)/2.0        # one sixteenth from destination
            y=(yd+y)/2.0
        return (x,y)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    net = None
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if os.path.exists(fname):
            net = read_npickle(fname)
        else:
            QtGui.QMessageBox.critical(
                        app, "Error opening file %s", fname,
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
        
    simgui = SimulationGui(net,fname=fname)
    simgui.show()
    try: sys.exit(app.exec_())
    except SystemExit: pass
