from pymote.algorithm import NodeAlgorithm
from pymote.algorithm import NetworkAlgorithm
from pymote.utils.tree import get_root_node, MissingTreeKey
from pymote.logger import logger
from pymote.conf import settings
from networkx import Graph
import networkx as nx
from environment import Environment
from channeltype import ChannelType
from node import Node
from numpy.random import rand
from numpy import array, pi


class Network(Graph):

    def __init__(self, environment=None, channelType=None, algorithms=(),
                 networkRouting=True):
        self._environment = environment or Environment()
        # assert(isinstance(self.environment,Environment))
        self.channelType = channelType or ChannelType(self._environment)
        self.pos = {}
        self.ori = {}
        self.labels = {}
        Graph.__init__(self)
        self._algorithms = ()
        self.algorithms = algorithms or settings.ALGORITHMS
        self.algorithmState = {'index': 0, 'step': 1, 'finished': False}
        self.outbox = []
        self.networkRouting = networkRouting
        logger.debug("Instance of Network has been initialized.")

    # TODO: incomplete add other properties
    def subgraph(self, nbunch, pos=None):
        if not pos:
            pos = self.pos
        H = Graph.subgraph(self, nbunch)
        for node in H:
            H.pos.update({node: pos[node][:2]})
            if len(pos[node]) > 2:
                H.ori.update({node: pos[node][2]})
            else:
                H.ori.update({node: self.ori[node]})
            H.labels.update({node: self.labels[node]})
        return H

    def nodes(self, data=False):
        """ Override, sort nodes by id, important for message ordering."""
        return list(sorted(self.nodes_iter(data=data), key=lambda k: k.id))

    @property
    def algorithms(self):
        """
        You can set algorithms by passing tuple of tuples that are in form
        (AlgorithmClass, params). AlgorithmClass must be subclass of Algorithm
        (NodeAlgorithm, NetworkAlgorithm) class.
        """
        return self._algorithms

    @algorithms.setter
    def algorithms(self, algorithms):
        self.reset()
        self._algorithms = ()
        if not isinstance(algorithms, tuple):
            raise PymoteNetworkError('algorithm')
        for algorithm in algorithms:
            if not (isinstance(algorithm, tuple) and
                    len(algorithm) == 2 and
                    (issubclass(algorithm[0], NodeAlgorithm) or
                     issubclass(algorithm[0], NetworkAlgorithm)) and
                    isinstance(algorithm[1], dict)):
                raise PymoteNetworkError('algorithm')
            self._algorithms += algorithm[0](self, **algorithm[1]),

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, environment):
        """ If net environment is changed all nodes are moved into and
            corresponding channelType environment must be changed also. """
        self._environment = environment
        self.channelType.environment = environment
        for node in self.nodes():
            self.remove_node(node)
            self.add_node(node)
        logger.warning('All nodes are moved into new environment.')

    def remove_node(self, node):
        """ Remove node from network. """
        Graph.remove_node(self, node)
        del self.pos[node]
        del self.labels[node]
        node.network = None
        logger.debug('Node with id %d is removed.' % node.id)

    def add_node(self, node=None, pos=None, ori=None, commRange=None):
        """
        Add node to network.
        
        Attributes:
          `node` -- node to add, default: new node is created
          `pos` -- position (x,y), default: random free position in environment
          `ori` -- orientation from 0 to 2*pi, default: random orientation
            
        """
        if (not node):
            node = Node(commRange=commRange)
        assert(isinstance(node, Node))
        if not node.network:
            node.network = self
        else:
            logger.warning('Node is already in another network, can\'t add.')
            return None

        pos = pos or self.find_random_pos(n=100)
        ori = ori or rand() * 2 * pi
        ori = ori % (2 * pi)

        if (self._environment.is_space(pos)):
            Graph.add_node(self, node)
            self.pos[node] = array(pos)
            self.ori[node] = ori
            self.labels[node] = str(node.id)
            logger.debug('Node %d is placed on position %s.' % (node.id, pos))
            self.recalculate_edges([node])
        else:
            logger.error('Given position is not free space.')
        return node

    def node_by_id(self, id_):
        """ Returns first node with given id. """
        for n in self.nodes():
            if (n.id == id_):
                return n
        logger.error('Network has no node with id %d.' % id)
        return None

    def get_current_algorithm(self):
        """ Try to return current algorithm based on algorithmState. """
        if len(self.algorithms) == 0:
            logger.warning('There is no algorithm defined in a network.')
            return None
        if self.algorithmState['finished']:
            if len(self.algorithms) > self.algorithmState['index'] + 1:
                self.algorithmState['index'] += 1
                self.algorithmState['step'] = 1
                self.algorithmState['finished'] = False
            else:
                return None
        return self.algorithms[self.algorithmState['index']]

    def reset(self):
        logger.info('Resetting network.')
        self.algorithmState = {'index': 0, 'step': 1, 'finished': False}
        self.reset_all_nodes()

    def show(self, savefig='', positions=None, edgelist=None, nodeColor='r', \
             show_labels=True):

        try:
            from matplotlib import pyplot as plt
        except ImportError:
            raise ImportError("Matplotlib required for show()")

        # TODO: environment when positions defined
        node_size = 30
        label_delta = array([10, 10])
        dpi = 100
        fig_size = tuple(array(self._environment.im.shape) / dpi)

        # figsize in inches
        # default matplotlibrc is dpi=80 for plt and dpi=100 for savefig
        plt.figure(figsize=fig_size, dpi=dpi)
        plt.imshow(self._environment.im, cmap='binary_r', vmin=0)
        if positions:
            # truncate positions to [x, y], i.e. lose theta
            for k, v in positions.items():
                positions[k] = v[:2]
            pos = positions
            net = self.subgraph(pos.keys())
        else:
            pos = self.pos
            net = self
        nx.draw_networkx_edges(net, pos, alpha=0.6, edgelist=edgelist)
        nx.draw_networkx_nodes(net, pos, node_size=node_size,
                               node_color=nodeColor, cmap='YlOrRd')
        if (show_labels):
            label_pos = {}
            for n in net.nodes():
                label_pos[n] = pos[n].copy() + label_delta
            nx.draw_networkx_labels(net, label_pos, labels=net.labels)
        # plt.axis('off')
        if savefig:
            plt.savefig(savefig)
        else:
            plt.show()

    def savefig(self, fname='network.png'):
        self.show(savefig=fname)

    def recalculate_edges(self, nodes=[]):
        """ Recalculate edges for given nodes or for all self.nodes().
        Edge between nodes n1 and n2 are added if both are
        ChannelType.in_comm_range of each other"""
        if(not nodes):
            nodes = self.nodes()
        for n1 in nodes:
            for n2 in self.nodes():
                if (n1 != n2):
                    if (self.channelType.in_comm_range(self, n1, n2)):
                        Graph.add_edge(self, n1, n2)
                    elif (Graph.has_edge(self, n1, n2)):
                        Graph.remove_edge(self, n1, n2)

    def add_edge(self):
        logger.warn('Edges are auto-calculated from channelType and commRange')

    def find_random_pos(self, n=100):
        """ Returns random position, position is free space in environment if
         it can find free space in n iterations """
        while (n > 0):
            pos = rand(self._environment.dim) * self._environment.im.shape
            if self._environment.is_space(pos):
                break
            n -= 1
        return pos

    def reset_all_nodes(self):
        for node in self.nodes():
            node.reset()
        logger.info('Resetting all nodes.')

    def communicate(self):
        """Pass all messages from node's outboxes to its neighbors inboxes."""
        # Collect messages
        for node in self.nodes():
            self.outbox.extend(node.outbox)
            node.outbox = []
        while self.outbox:
            message = self.outbox.pop()
            if (message.destination == None and message.nexthop == None):
                # broadcast
                self.broadcast(message)
            elif (message.nexthop != None):
                # Node routing
                try:
                    self.send(message.nexthop, message)
                except PymoteMessageUndeliverable, e:
                    print e.message
            elif (message.destination != None):
                # Destination is neighbor
                if (message.source in self.nodes() and
                    message.destination in self.neighbors(message.source)):
                    self.send(message.destination, message)
                elif (self.networkRouting):
                # Network routing
                # TODO: program network routing so it goes hop by hop only
                #       in connected part of the network
                    self.send(message.destination, message)
                else:
                    raise PymoteMessageUndeliverable('Can\'t deliver message.',
                                                      message)

    def broadcast(self, message):
        if message.source in self.nodes():
            for neighbor in self.neighbors(message.source):
                neighbors_message = message.copy()
                neighbors_message.destination = neighbor
                self.send(neighbor, neighbors_message)
        else:
            raise PymoteMessageUndeliverable('Source not in network. \
                                             Can\'t broadcast', message)

    def send(self, destination, message):
        logger.debug('Sending message from %s to %s.' %
                      (repr(message.source), destination))
        if destination in self.nodes():
            destination.push_to_inbox(message)
        else:
            raise PymoteMessageUndeliverable('Destination not in network.',
                                             message)

    def get_dic(self):
        """ Return all network data in form of dictionary. """
        algorithms = {'%d %s' % (ind, alg.name): 'active'
                      if alg == self.algorithms[self.algorithmState['index']]
                      else '' for ind, alg in enumerate(self.algorithms)}
        pos = {n: 'x: %.2f y: %.2f theta: %.2f deg' %
               (self.pos[n][0], self.pos[n][1], self.ori[n] * 180. / pi)
               for n in self.nodes()}
        # TODO: environment, channeltype
        return {'nodes': pos,
                'algorithms': algorithms,
                'algorithmState': {'name':
                                   self.get_current_algorithm().name
                                   if algorithms else '',
                                  'step': self.algorithmState['step'],
                                  'finished': self.algorithmState['finished']}}

    def get_tree_net(self, treeKey):
        """Returns new network with edges that are not in a tree removed."""
        # TODO: levels not needed?
        try:
            nodesToCheck = [(get_root_node(self, treeKey), 0)]
        except MissingTreeKey:
            return None
        if nodesToCheck[0][0] == None:
            # TODO: raise exception?
            return
        edgelist = []
        levels = [0] * len(self.nodes())  # level of node in tree, root is 0
        while nodesToCheck:
            (node, level) = nodesToCheck.pop()
            edgelist += [(node, child) for child in
                         node.memory[treeKey]['children']
                         if child in self.nodes()]
            levels[self.nodes().index(node)] = level
            nodesToCheck += [(child, level + 1) for child in
                             node.memory[treeKey]['children']
                             if child in self.nodes()]

        treeNet = self.copy()
        for e in treeNet.edges():
            if e not in edgelist and (e[1], e[0]) not in edgelist:
                treeNet.remove_edge(*e)
        return treeNet


class PymoteMessageUndeliverable(Exception):
    def __init__(self, e, message):
        self.e = e
        self.message = message

    def __str__(self):
        return self.e + repr(self.message)


class PymoteNetworkError(Exception):
    def __init__(self, type_):
        if type_ == 'algorithm':
            self.message = ('\nAlgorithms must be tuple of tuples in form: '
                            '(AlgorithmClass, params_dictionary).'
                            'AlgorithmClass should be subclass of '
                            'NodeAlgorithm or NetworkAlgorithm.')
        else:
            self.message = ''

    def __str__(self):
        return self.message
