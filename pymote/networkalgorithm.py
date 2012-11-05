from pymote.algorithm import Algorithm
class NetworkAlgorithm(Algorithm):
    """ NetworkAlgorithm class. 
        This class is used as base class holding real network algorithm 
        classes in its __subclassess__ for easy instantiation
        Method __init__ and run should be implemented in subclass. """
    
    def run(self):
        raise NotImplementedError
        
