from pymote.message import Message
from pymote.logger import logger



class Algorithm(object):
    
    required_params = ()
    default_params = {}

    def __init__(self, network, **kwargs):
        self.network = network
        self.name = self.__class__.__name__
        logger.debug('Instance of %s class has been initialized.' %
                    self.name)
    
        for default_param in self.default_params.keys():
            if default_param in self.required_params:
                raise PymoteAlgorithmException('Default param cannot be'
                                               'required param.')
        
        for required_param in self.required_params:
            if required_param not in kwargs.keys():
                raise PymoteAlgorithmException('Missing required param.')
        
        # set default params
        for dp,val in self.default_params.items():
            self.__setattr__(dp,val)
            
        # override default params
        for kw,arg in kwargs.items():
            self.__setattr__(kw,arg)
            

class NodeAlgorithm(Algorithm):
    """ NodeAlgorithm class. 
        This class is used as base class and specific algorithm should be its 
        subclass. In subclass these functions and attributes should be defined:
        - class attribute STATUS - dictionary in which keys are all possible 
          node statuses and values are functions defining what node should do 
          if in that status. STATUS must be written at the bottom after all
          functions are defined
        - all functions in STATUS.values() should be defined
        - initializer: (optionally) Pass INI message to nodes that should 
          start the algorithm and set some attributes needed by the specific 
          algorithm
        As indication of global termination of algorithm function should 
        optionally return true."""
        
    INI = 'initialize'
    STATUS = {}
    
    
    def initializer(self):
        """ Pass INI message to certain nodes in network based on type. """
        
        node = self.network.nodes()[0]
        self.network.outbox.insert(0,Message(header=NodeAlgorithm.INI, 
                                             destination=node))
        for node in self.network.nodes():
            node.status = 'IDLE'
            
    def step(self, node):
        """ Executes one step of the algorithm for given node. """
        message = node.receive()
        if message:
            if (message.destination==None or message.destination==node):
                # when destination is None it is broadcast message
                return self._process_message(node,message)
            elif (message.nexthop==node.id):
                self._forward_message(node,message)
            
    def _forward_message(self, node, message):
        try:
            message.nexthop = node.memory['routing'][message.destination]
        except KeyError:
            logger.warn('Missing routing table or destination node not in it.')
        else:
            node.send(message)

    def _process_message(self,node,message):
        return self.__class__.STATUS.get(node.status,self.statuserr)(self,
                                                                    node,
                                                                    message)
    
    def statuserr(self,node,message):
        logger.error('Can\'t handle status %s.' % node.status)
        

class NetworkAlgorithm(Algorithm):
    """ NetworkAlgorithm class. 
        This class is used as base class holding real network algorithm 
        classes in its __subclassess__ for easy instantiation
        Method __init__ and run should be implemented in subclass. """
    
    def run(self):
        raise NotImplementedError
        
            
class PymoteAlgorithmException(Exception):
    pass
    