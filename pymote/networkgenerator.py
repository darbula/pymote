from networkx import is_connected
from numpy.core.numeric import Inf
from pymote.network import Network
from pymote.logger import logger
from conf import settings


class NetworkGenerator(object):

    def __init__(self, n_count=None, n_min=0, n_max=Inf, connected=True,
                 environment=None, degree=None, comm_range=None):
        """
        Arguments:
            n_count (int):
                number of nodes, if None settings.N_COUNT is used
            n_min (int):
                minimum number of nodes
            n_max (int):
                maximum number of nodes
            connected (bool):
                if True network must be fully connected
            environment (:class:`Environment`):
                environment in which the network should be created, if None
                settings.ENVIRONMENT is used
            degree (int):
                average number of neighbors per node
            comm_range (int):
                nodes communication range, if None settings.COMM_RANGE is used
            
        Basic usage:
        
        >>> net_gen = NetworkGenerator()
        >>> net = net_gen.generate_random_network()
        
        """
        self.n_count=n_count if n_count else settings.N_COUNT
        if self.n_count<n_min or self.n_count>n_max:
            raise NetworkGeneratorException('Number of nodes must be between '
                                            'n_min and n_max.')
        self.n_min = n_min
        self.n_max = n_max
        self.connected = connected
        self.environment = environment
        self.degree = degree
        self.comm_range = comm_range

    def _create_modify_network(self, net=None, direction=1):
        """Helper method for creating new or modifying given network.
        
        Arguments:
            net (int):
                network to modify, if None create from scratch
            direction:
                if 1 new network should be more dense for -1 less dense
                
        """
        if net is None:
            net = Network(environment=self.environment)
            for _n in range(self.n_count):
                net.add_node(commRange=self.comm_range)
        else:
            if direction==1:
                if len(net)<self.n_max:
                    net.add_node()
                    logger.debug("Adding node, number of nodes: %d"
                                 % (len(net)+1))
                elif not self.comm_range:
                    logger.debug("Increasing commRange to %d"
                                 % (net.nodes()[0].commRange+1))
                    for node in net.nodes():
                        node.commRange += 1
                else:
                    return None
            else:
                if len(net)>self.n_min and len(net)>1:
                    net.remove_node(net.nodes()[0])
                    logger.debug("Removing node, nodes left: %d"
                                 % (len(net)-1))
                elif not self.comm_range:
                    logger.debug("Decreasing commRange to %d"
                                 % (net.nodes()[0].commRange+1))
                    for node in net.nodes():
                        node.commRange -= 1
                else:
                    return None
        return net
    
    def _are_conditions_satisfied(self, net):
        if self.connected and not is_connected(net):
            logger.debug("Not connected")
            return 1
        elif self.degree and (net.avg_degree()<self.degree):
            logger.debug("Degree too small %f" % net.avg_degree())
            return 1
        elif self.degree and (net.avg_degree()>self.degree+1):
            logger.debug("Degree too big %f" % net.avg_degree())
            return -1
        return 0
    
    def generate_random_network(self):
        """Basic method: generates network with randomly positioned nodes."""
        #TODO: try some more advanced algorithm for situation when
        # both connected network and too small degree are needed
        #TODO: increase step for commRange adjustment
        net = None
        direction=[0]
        while True:
            net=self._create_modify_network(net, direction[-1])
            if not net:
                break
            direction.append(self._are_conditions_satisfied(net))
            if len(direction)>1000:
                break
            if direction[-1]==0:
                if len(direction)>1:
                    logger.warning("Exact parameters could not be satisfied.\n"
                                   "Number of nodes: %d\ncommRange: %d"
                                   % (len(net), net.nodes()[0].commRange))
                return net
            
        logger.error("Could not generate connected network with given "
                     "parameters. Try removing and/or modifying some of "
                     "them.")
        
       
class NetworkGeneratorException(Exception):
    pass
