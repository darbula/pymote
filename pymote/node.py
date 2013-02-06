from pymote.utils.memory.positions import Positions
from copy import deepcopy
from pymote.utils.memory import MemoryStructure
from pymote.logger import logger
from pymote.sensor import CompositeSensor
#from pymote.actuator import *
from pymote.conf import settings


class Node(object):
    """ Node class. """
    cid = 1
    
    def __init__(self, network=None, commRange=None, sensors=None):
        self.compositeSensor = CompositeSensor(sensors or settings.SENSORS)
        #self.compositeActuator = CompositeActuator(actuators or settings.ACTUATORS)
        self.network = network
        self._commRange = commRange or settings.COMM_RANGE
        self.id = self.__class__.cid
        self.__class__.cid += 1
        self._inboxDelay = True
        self.reset()
        
    
    def __repr__(self):
        return "<Node id=%s>" % self.id
        #return "<Node id=%s at 0x%x>" % (self.id, id(self))

    def __deepcopy__(self, memo):
        return self
        
    def reset(self):
        self.outbox = []
        self._inbox = []
        self.status = ''
        self.memory = {}
    
    def send(self, message):
        message.source = self
        message.destination = isinstance(message.destination,list) and message.destination or [message.destination]
        for destination in message.destination:
            logger.debug('Node %d sent message %s.' % (self.id,message.__repr__()))
            m = message.copy()
            m.destination = destination
            self.outbox.insert(0,m)

    def receive(self):
        """ 
        Pop message from inbox but only if it has been there at least one step.
        
        Messages should be delayed for one step for visualization purposes.
        Messages are processed without delay only if they are pushed into empty 
        inbox. So if inbox is empty when push_to_inbox is called _inboxDelay is
        set to True. 
        """
        if self._inbox and not self._inboxDelay:
            message = self._inbox.pop()
            logger.debug('Node %d received message %s' % (self.id,message.__repr__()))
        else:
            message = None
        self._inboxDelay = False
        return message
    
    @property
    def inbox(self):
        return self._inbox

    def push_to_inbox(self,message):
        #TODO: for optimization remove _inboxDelay when not visualizing
        self._inboxDelay = self._inboxDelay or not self._inbox
        self._inbox.insert(0,message)

    @property
    def commRange(self):
        return self._commRange
    
    @commRange.setter
    def commRange(self,commRange):
        self._commRange = commRange
        self.network.recalculate_edges([self])
    
    @property
    def warnings(self):
        """ Special field in memory used to log warnings from algorithms. """
        if not self.memory.has_key('warnings'):
            self.memory['warnings'] = []
        return self.memory['warnings']
    
    @warnings.setter
    def warnings(self, warning):
        assert isinstance(warning, str)
        if not self.memory.has_key('warnings'):
            self.memory['warnings'] = [warning]
        else:
            self.memory['warnings'].append(warning)
                
    def get_dic(self):
        return {'1. info':{'id':self.id,
                    'status':self.status,
                    'position':self.network.pos[self],
                    'orientation':self.network.ori[self]},
                '2. communication':{'range':self.commRange,
                                    'inbox':self.box_as_dic('inbox'),
                                    'outbox':self.box_as_dic('outbox')},
                '3. memory':self.memory,
                '4. sensors':{sensor.name(): '%s(%.3f)' % 
                              (sensor.probabilityFunction.name,sensor.probabilityFunction.scale) if hasattr(sensor,'probabilityFunction') else ('',0)  
                              for sensor in self.compositeSensor.sensors}}
                
    
    def box_as_dic(self, box):
        messagebox = self.__getattribute__(box)
        dic = {}
        for i,message in enumerate(messagebox):
            dic.update({'%d. Message' % (i+1,):{'1 header':message.header,
                                              '2 source':message.source,
                                              '3 destination':message.destination,
                                              '4 data':message.data}})
        return dic
            
        
