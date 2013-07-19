#@PydevCodeAnalysisIgnore
import unittest
from numpy.core.numeric import Inf
from pymote.networkgenerator import NetworkGenerator, NetworkGeneratorException
from pymote.conf import settings
from pymote.environment import Environment2D


class TestNetworkGeneration(unittest.TestCase):

    def setUp(self):
        # Raises NetworkGeneratorException
        # returns None
        # else expected number of nodes
        env = Environment2D(shape=(600,600))
        self.in_out = [
                  # default N_COUNT and COMM_RANGE and ENVIRONMENT should be compatible
                  ({"n_count": None, "n_min": 0, "n_max": Inf, "connected": True, "environment": None, "degree": None, "comm_range": None}, range(settings.N_COUNT,settings.N_COUNT*2+1)),  
                  # regular default params
                  ({"n_count": 100, "n_min": 0, "n_max": Inf,  "connected": True, "environment": env,  "degree": None, "comm_range": 100},  range(100,1001)),
                  
                  ############## connected True degree False
                  # increase node number
                  ({"n_count": 10, "n_min": 0, "n_max": Inf, "connected": True, "environment": env, "degree": None, "comm_range": 100},  range(11,301)),
                  # increase commRange
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": None, "comm_range": None}, 10),
                  
                  ############## connected True degree True
                  # increase node number
                  ({"n_count": 10, "n_min": 0, "n_max": 200, "connected": True, "environment": env, "degree": 11, "comm_range": 100},  range(10,201)),
                  # increase commRange
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": 9,  "comm_range": None}, 10),
                  # low degree with connected, alternating directions problem
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": 3,  "comm_range": 30},   None),
                  
                  ############## connected False degree True
                  # increase node number
                  ({"n_count": 10, "n_min": 0, "n_max": 200, "connected": False, "environment": env, "degree": 8,  "comm_range": 100},   range(10,201)),
                  # increase commRange
                  ({"n_count": 10, "n_min": 0, "n_max": 200, "connected": False, "environment": env, "degree": 11, "comm_range": None},  range(10,201)),

                  # low degree 
                  ({"n_count": 10, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": 3,  "comm_range": 100},    range(10,101)),
                  # degree too high for node number
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": False, "environment": env, "degree": 10,   "comm_range": None}, 'NetworkGeneratorException'),
                  ({"n_count": 11, "n_min": 0, "n_max": 10,  "connected": False, "environment": env, "degree": None, "comm_range": None}, 'NetworkGeneratorException'),
                  ({"n_count": 9, "n_min": 10, "n_max": 10,  "connected": False, "environment": env, "degree": None, "comm_range": None}, 'NetworkGeneratorException'),
                  
                  ############## connected False degree False - no need for modifying initially created network 
                  ({"n_count": 10, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": None,  "comm_range": 100},  10),
                  ({"n_count": 20, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": None,  "comm_range": None}, 20),
                  ({"n_count": 30, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": None,  "comm_range": 30},   30),
              ]
        

    def test_random_generation(self):
        """Test different random generation parameters"""
        for io in self.in_out:
            if io[1]=='NetworkGeneratorException':
                self.assertRaises(NetworkGeneratorException, NetworkGenerator, io[0])
                continue
            net_gen = NetworkGenerator(**io[0])
            if io[1]==None:
                self.assertEqual(None, net_gen.generate_random_network())
            else:
                expected_nodes_number = [io[1]] if not isinstance(io[1], list) else io[1]
                net = net_gen.generate_random_network()
                self.assertNotEquals(net, None, "Network not generated with following params:\n%s" % str(io[0]))
                self.assertIn(len(net), expected_nodes_number, "Unexpected number of nodes with following params:\n%s" % str(io[0]))
            
