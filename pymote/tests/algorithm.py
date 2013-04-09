import unittest
from pymote.networkgenerator import NetworkGenerator
from pymote.algorithm import Algorithm, NodeAlgorithm, NetworkAlgorithm,\
                             PymoteAlgorithmException
from pymote.network import PymoteNetworkError


class TestAlgorithmsSetter(unittest.TestCase):
    
    def setUp(self):
        
        class SomeNodeAlgorithm(NodeAlgorithm):
            required_params = ('rp1',
                               'rp2',
                               'rp3')
            default_params = {'dp1':'dp1_value',
                              'dp2':'dp2_value',
                              'dp3':'dp3_value'}
        
        class SomeNetworkAlgorithm(NetworkAlgorithm):
            required_params = ('rp1',
                               'rp2',
                               'rp3')
            default_params = {'dp1':'dp1_value',
                              'dp2':'dp2_value',
                              'dp3':'dp3_value'}
            
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.algorithms_ok = ((SomeNodeAlgorithm,
                              {'rp1': 1,
                               'rp2': 2,
                               'rp3': 3,
                               }),
                
                              (SomeNetworkAlgorithm,
                              {'rp1': 1,
                               'rp2': 2,
                               'rp3': 3,
                               }),
                              )

        self.algorithms_wrong_format1 = [(SomeNodeAlgorithm, {}),]
        self.algorithms_wrong_format2 = ((SomeNodeAlgorithm),)
        self.algorithms_wrong_base_class = ((Algorithm, {}),)
        self.algorithms_missing_req_param = ((SomeNodeAlgorithm,
                                              {'rp1': 1,
                                               }),
                                              (SomeNetworkAlgorithm,
                                              {'rp1': 1,
                                               }),
                                              )

                  
    def test_setter(self):
        """Test different algorithm initialization formats."""
        self.set_algorithms(self.algorithms_ok)
        self.assertRaises(PymoteNetworkError, self.set_algorithms, self.algorithms_wrong_format1)
        self.assertRaises(PymoteNetworkError, self.set_algorithms, self.algorithms_wrong_format2)
        self.assertRaises(PymoteNetworkError, self.set_algorithms, self.algorithms_wrong_base_class)
        self.assertRaises(PymoteAlgorithmException, self.set_algorithms, self.algorithms_missing_req_param)
 
    def set_algorithms(self, algorithms):
        self.net.algorithms = algorithms
    
    
