import unittest
from pymote.node import Node
from pymote.network import Network
from pymote.sensor import NeighborsSensor


class TestSensor(unittest.TestCase):
    
    def test_node_without_network(self):
        """Test if node without network raises exception on read sensor."""
        node = Node()
        self.assertRaises(Exception, node.compositeSensor.read)
        self.assertRaises(Exception, node.compositeSensor.read)
   
    def test_read(self):
        """Test read compositeSensor"""
        net = Network()
        node = net.add_node()
        node.compositeSensor.read()
    
    def test_set_compositeSensor(self):
        """Test setting compositeSensors on a node"""
        net = Network()
        node = net.add_node()
        node.compositeSensor = ('AoASensor',NeighborsSensor)
        self.assertTrue(len(node.compositeSensor.sensors)==2)
        readings = node.compositeSensor.read()
        self.assertTrue('AoA' in readings.keys() and 'Neighbors' in readings.keys())
        
        #TODO: check normal distribution
