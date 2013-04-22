"""
Sensors provide a way for node to interact with its environment.

Sensors can also be used to satisfy algorithm prerequisites. For example
if algorithm depends on the assumption that all nodes know who their neighbors
are then nodes should be equipped with :class:`NeighborsSensor`.

Generally sensors should incorporate some model of measurement insecurity that
is inherent in real world sensors. This is implemented as a
:class:`ProbabilityFunction`.

"""

from pymote.conf import settings
from numpy import arctan2, pi, sqrt
import inspect


class Sensor(object):

    """
    Abstract base class for all Sensors.
    
    Sensor provides a certain capability for a node, information about the
    outside world. It could could be a capability to detect neighbors, distance
    to them or to get the environment temperature.
    
    """

    def __init__(self):
        self.probabilityFunction = None

    def name(self):
        return self.__class__.__name__

    def read(self):
        """This method should be overriden in subclass."""
        pass


def node_in_network(fun):
    """Decorator function that checks if node is in network."""
    def f(sensor, node):
        if not node.network:
            raise Exception('Cannot take a sensor reading if node is'
                            ' outside of a network.')
        return fun(sensor, node)
    return f


class NeighborsSensor(Sensor):

    """Provides list of node's neighbors."""

    @node_in_network
    def read(self, node):
        return {'Neighbors': node.network.neighbors(node)}


class AoASensor(Sensor):

    """Provides azimuth between node and its neighbors."""

    def __init__(self):
        self.probabilityFunction = ProbabilityFunction('AOA_PF_PARAMS')

    @node_in_network
    def read(self, node):
        network = node.network
        measurements = {}
        p = network.pos[node]
        o = network.ori[node]
        for neighbor in network.neighbors(node):
            v = network.pos[neighbor] - p
            measurement = (arctan2(v[1], v[0]) - o) % (2 * pi)
            measurement = self.probabilityFunction.getNoisyReading(measurement)
            measurements.update({neighbor: measurement})
        return {'AoA': measurements}


class DistSensor(Sensor):

    """Provides distance between node and its neighbors."""

    def __init__(self):
        self.probabilityFunction = ProbabilityFunction('DIST_PF_PARAMS')

    @node_in_network
    def read(self, node):
        network = node.network
        measurements = {}
        p = network.pos[node]
        for neighbor in network.neighbors(node):
            pn = network.pos[neighbor]
            measurement = sqrt(sum(pow(p - pn, 2)))
            measurement = self.probabilityFunction.getNoisyReading(measurement)
            measurements.update({neighbor: measurement})
        return {'Dist': measurements}


class TruePosSensor(Sensor):

    """Provides node's true position."""

    @node_in_network
    def read(self, node):
        return {'TruePos': node.network.pos[node]}


class CompositeSensor(object):

    """
    Wrap multiple sensors, coalesce results and return composite readout.
    
    This class is not a sensor itself, i.e. subclass of :class:`Sensor`,
    instead it serves as a placeholder for multiple sensors that can be
    attached to a :class:`Node`.
    
    """

    def __init__(self, node, componentSensors=None):
        """
        Arguments:
            node (:class:`Node`):
                Node that has this composite sensor is attached to.
            componentSensors (tuple):
                Tuple of :class:`Sensor` subclasses or their class names.
            
        """
        self.node = node
        self._sensors = ()
        self.sensors = componentSensors or ()

    @property
    def sensors(self):
        return self._sensors

    @sensors.setter
    def sensors(self, sensors):
        # instantiate sensors passed by class name
        for cls in Sensor.__subclasses__():
            if (cls.__name__ in sensors):
                self._sensors += cls(),
        # instantiate sensors passed by class
        for cls in sensors:
            if inspect.isclass(cls) and issubclass(cls, Sensor):
                self._sensors += cls(),

    def read(self):
        measurements = {}
        for sensor in self._sensors:
            measurements.update(sensor.read(self.node))
        return measurements


class ProbabilityFunction(object):

    """Provides a way to get noisy reading."""

    def __init__(self, settings_key):
        """
        Arguments:
            settings_key: a settings parameter
            
        """
        self.pf = getattr(settings, settings_key)['pf']  # class or gen object
        self.name = self.pf.__class__.__name__
        self.scale = getattr(settings, settings_key)['scale']

    def getNoisyReading(self, value):
        return self.pf.rvs(scale=self.scale, loc=value)
