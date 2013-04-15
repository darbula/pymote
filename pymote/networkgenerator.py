from networkx import is_connected
from pymote.network import Network
from pymote.logger import logger
from numpy.lib.function_base import average
from numpy.core.numeric import Inf


class NetworkGenerator:
    
    def __init__(self, n_count=None, n_min=0, n_max=Inf, connected=True, environment=None,
                 degree=None):
        self.n_count = n_count
        self.n_min = n_min
        self.n_max = n_max
        self.connected= connected
        self.environment = environment
        self.degree = degree
        
        self.generate = self.generate_random_network
        if self.degree:
            self.generate = self.generate_degree_network
        
        
    def generate_random_network(self):
        for i in range(100): #@UnusedVariable
            net = Network(environment=self.environment)
            for j in range(self.n_count): #@UnusedVariable
                net.add_node()
            if is_connected(net):
                return net
        logger.error("Could not generate connected network with %d nodes.\n"
                     "You can try to increase number of nodes or commRange." %
                     self.n_count)
        #TODO: increase comm_range to value that is enough for connected network
        return None
    
    
    def generate_degree_network(self):
        n_min_condition = degree_condition = connected_condition = i = 0
        while i<10:
            net = Network(environment=self.environment)
            i+=1
            logger.debug('Generating, try %d.' % i)
            while not len(net.nodes()) or average(net.degree().values())<self.degree and len(net.nodes())<self.n_max:
                net.add_node()
                logger.debug('Current degree %f.' % average(net.degree().values()))
            if len(net.nodes())<self.n_min:
                n_min_condition+=1
            elif net.degree<self.degree:
                degree_condition+=1
            elif not is_connected(net):
                connected_condition+=1
            else:
                return net
            
        logger.error('Could not generate network.'
                     ' n_min is too high for wanted degree (%d)'
                     ' cannot reach wanted degree (%d)'
                     ' network is not connected (%d)' % 
                     (n_min_condition,degree_condition,connected_condition))
        #TODO: increase comm_range to value that is enough for connected network
        return None