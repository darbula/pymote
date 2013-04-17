import unittest
from pymote.algorithms.niculescu2003.trilaterate import Trilaterate
from pymote.simulation import Simulation
from pymote.sensor import TruePosSensor
from pymote.networkgenerator import NetworkGenerator
from pymote.algorithms.niculescu2003.dvhop import DVHop

class TestNiculescu2003(unittest.TestCase):
    
    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = ((DVHop,{'truePositionKey':'tp',
                                  'hopsizeKey':'hs',
                                  'dataKey':'I'
                                  }),
                          (Trilaterate,{'truePositionKey':'tp',
                                        'hopsizeKey':'hs',
                                        'positionKey':'pos',
                                        'dataKey':'I'}), 
                          )
        for node in self.net.nodes()[:10]:
            node.compositeSensor = (TruePosSensor,)
        
    def test_niculescu2003_sim(self):
        """Test niculescu2003 default simulation."""
        sim = Simulation(self.net)
        sim.run()
        for node in self.net.nodes():
            self.assertTrue(len(node.memory.get('pos',[None,None]))==2\
                            or node.memory.has_key('tp'))