import unittest
from numpy.core.numeric import Inf
from pymote.networkgenerator import NetworkGenerator, NetworkGeneratorException
from pymote.conf import settings
from pymote.environment import Environment2D

#@PydevCodeAnalysisIgnore
class TestNetworkGeneration(unittest.TestCase):

    def setUp(self):
        #-1 Raises exception
        # else expected number of nodes
        env = Environment2D(shape=(600,600))
        self.in_out = [
                  # default N_COUNT and COMM_RANGE and ENVIRONMENT should be compatible
                  ({"n_count": None, "n_min": 0, "n_max": Inf, "connected": True, "environment": None, "degree": None, "comm_range": None}, range(settings.N_COUNT,settings.N_COUNT*2)),  
                  # regular default params
                  ({"n_count": 100, "n_min": 0, "n_max": Inf,  "connected": True, "environment": env,  "degree": None, "comm_range": 100},  range(100,200)),
                  
                  ############## connected True degree False
                  # increase node number
                  ({"n_count": 10, "n_min": 0, "n_max": Inf, "connected": True, "environment": env, "degree": None, "comm_range": 100},  range(11,300)),
                  # increase commRange
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": None, "comm_range": None}, 10),
                  
                  ############## connected True degree True
                  # increase node number
                  ({"n_count": 10, "n_min": 0, "n_max": 200, "connected": True, "environment": env, "degree": 11, "comm_range": 100},  range(10,200)),
                  # increase commRange
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": 9,  "comm_range": None}, 10),
                  # low degree with connected, alternating directions problem
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": 3,  "comm_range": 30},   -1),
                  # degree too high for node number
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": True, "environment": env, "degree": 10, "comm_range": None}, -1),
                  
                  ############## connected False degree True
                  # increase node number
                  ({"n_count": 10, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": 8,  "comm_range": 100},   range(10,100)),
                  # increase commRange
                  ({"n_count": 10, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": 21, "comm_range": None},  range(10,100)),
                  # low degree 
                  ({"n_count": 10, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": 3,  "comm_range": 100},    range(10,30)),
                  # degree too high for node number
                  ({"n_count": 10, "n_min": 0, "n_max": 10,  "connected": False, "environment": env, "degree": 10,  "comm_range": None}, -1),
                  
                  ############## connected False degree False - no need for modifying initially created network 
                  ({"n_count": 10, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": None,  "comm_range": 100},  10),
                  ({"n_count": 20, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": None,  "comm_range": None}, 20),
                  ({"n_count": 30, "n_min": 0, "n_max": 100, "connected": False, "environment": env, "degree": None,  "comm_range": 30},   30),
              ]
        

    def test_random_generation(self):
        """Try different setups and check output."""
        for io in self.in_out:
            net_gen = NetworkGenerator(**io[0])
            if io[1]==-1:
                self.assertEqual(None, net_gen.generate_random_network())
            else:
                expected_nodes_number = [io[1]] if not isinstance(io[1], list) else io[1]
                net = net_gen.generate_random_network()
                self.assertNotEquals(net, None, "Network not generated with following params:\n%s" % str(io[0]))
                self.assertIn(len(net), expected_nodes_number, "Unexpected number of nodes with following params:\n%s" % str(io[0]))
            
        #TODO:try with n_count>n_max or woth <n_min
