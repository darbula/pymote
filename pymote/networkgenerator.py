from networkx import is_connected
from numpy.core.numeric import Inf
from pymote.network import Network
from pymote.logger import logger
from conf import settings
from numpy import sign


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
        if degree and degree>=n_max:
            raise NetworkGeneratorException('Degree % d must be smaller than '
                                            'maximum number of nodes %d.'
                                            % (degree, n_max))
        #TODO: optimize recalculation of edges on bigger commRanges
        if degree and degree>16 and n_count!=Inf:
            logger.warning("Generation could be slow for large degree"
                           "parameter with bounded n_max.")
        self.n_min = n_min
        self.n_max = n_max
        self.connected = connected
        self.environment = environment
        self.degree = degree
        self.comm_range = comm_range

    def _create_modify_network(self, net=None, step=1):
        """Helper method for creating new or modifying given network.
        
        Arguments:
            net (int):
                network to modify, if None create from scratch
            step:
                if >0 new network should be more dense for <0 less dense
                
        """
        if net is None:
            net = Network(environment=self.environment)
            for _n in range(self.n_count):
                net.add_node(commRange=self.comm_range)
        else:
            if step>0:
                if len(net)<self.n_max:
                    net.add_node()
                    logger.debug("Added node, number of nodes: %d"
                                 % len(net))
                elif not self.comm_range:
                    for node in net.nodes():
                        node.commRange += step
                    logger.debug("Increased commRange to %d"
                                 % node.commRange)
                else:
                    return None
            else:
                if len(net)>self.n_min and len(net)>1:
                    net.remove_node(net.nodes()[0])
                    logger.debug("Removed node, nodes left: %d"
                                 % len(net))
                elif not self.comm_range:
                    for node in net.nodes():
                        node.commRange += step
                    logger.debug("Decreased commRange to %d"
                                 % net.nodes()[0].commRange)
                else:
                    return None
        return net
    
    def _are_conditions_satisfied(self, net):
        cr = net.nodes()[0].commRange
        if self.connected and not is_connected(net):
            logger.debug("Not connected")
            return round(0.2*cr)
        elif self.degree:
            logger.debug("Degree not satisfied %f" % net.avg_degree())
            diff = self.degree-net.avg_degree()
            return round((sign(diff)*(round(diff)*2)**2)*cr/100)
        return 0
    
    def generate_random_network(self):
        """Basic method: generates network with randomly positioned nodes."""
        #TODO: try some more advanced algorithm for situation when
        # both connected network and too small degree are needed
        # that is agnostic to actual dimensions of the environment
        net = None
        steps = [0]
        while True:
            net = self._create_modify_network(net, steps[-1])
            if not net:
                break
            steps.append(self._are_conditions_satisfied(net))
            if len(steps)>1000:
                break
            if steps[-1]==0:
                return net
            
        logger.error("Could not generate connected network with given "
                     "parameters. Try removing and/or modifying some of "
                     "them.")
        
       
class NetworkGeneratorException(Exception):
    pass
