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
            
            
class PymoteAlgorithmException(Exception):
    pass