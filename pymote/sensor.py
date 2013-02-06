from pymote.conf import settings
from numpy import arctan2,pi,sqrt
from pymote.logger import logger
import inspect


class Sensor(object):
    def __init__(self):
        self.probabilityFunction = None
    def read(self):
        raise NotImplementedError
    def name(self):
        return self.__class__.__name__
        

class AoASensor(Sensor):

    def __init__(self):
        self.probabilityFunction = ProbabilityFunction('AOA_PF_PARAMS')
        
    def read(self, node):
        if not node.network:
            logger.warning('Cannot take AoA reading if node is outside of network.')
            return {}
        network = node.network
        measurements = {}
        p = network.pos[node]
        o = network.ori[node]
        for neighbor in network.neighbors(node):
            v = network.pos[neighbor] - p
            measurement = (arctan2(v[1],v[0])-o)%(2*pi)
            measurement = self.probabilityFunction.getNoisyReading(measurement)
            measurements.update({neighbor:measurement})
        return {'AoA':measurements}  
    

class DistSensor(Sensor):
    
    def __init__(self):
        self.probabilityFunction = ProbabilityFunction('DIST_PF_PARAMS')
    
    def read(self, node):
        if not node.network:
            logger.warning('Cannot take Dist reading if node is outside of network.')
            return {}
        network = node.network
        measurements = {}
        p = network.pos[node]
        for neighbor in network.neighbors(node):
            pn = network.pos[neighbor]
            measurement = sqrt(sum(pow(p-pn,2)))
            measurement = self.probabilityFunction.getNoisyReading(measurement)
            measurements.update({neighbor:measurement})
        return {'Dist':measurements}
    

class TruePosSensor(Sensor):
    
    def read(self, node):
        if not node.network:
            logger.warning('Cannot take TruePos reading if node is outside of network.')
            return None
        return {'TruePos': node.network.pos[node]}

    
class CompositeSensor(object):
    """ Wrap multiple component sensors, coalesce the results, and return
        the composite readout. """

    def __init__(self, componentSensors=None):
        """ componentSensors can be tuple of classes or class names """ 
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
            if inspect.isclass(cls) and issubclass(cls,Sensor):  
                self._sensors += cls(),

    def read(self, node):
        measurements = {}
        for sensor in self._sensors:
            measurements.update(sensor.read(node))
        return measurements
    
    
    
class ProbabilityFunction(object):

    def __init__(self, settings_key):
        self.pf = getattr(settings,settings_key)['pf'] # class or gen object
        self.name = self.pf.__class__.__name__ 
        self.scale = getattr(settings,settings_key)['scale'] 
        
    def getNoisyReading(self, value):
        return self.pf.rvs(scale=self.scale,loc=value)  
    
