from pymote.logger import logger
from pymote.sensor import CompositeSensor
from pymote.conf import settings
import logging
import collections


class Node(object):

    cid = 1

    def __init__(self, network=None, commRange=None, sensors=None, **kwargs):
        self._compositeSensor = CompositeSensor(self, sensors or
                                                settings.SENSORS)
        self.network = network
        self._commRange = commRange or settings.COMM_RANGE
        self.id = self.__class__.cid
        self.__class__.cid += 1
        self._inboxDelay = True
        self.reset()

    def __repr__(self):
        return "<Node id=%s>" % self.id
        # return "<Node id=%s at 0x%x>" % (self.id, id(self))

    def __deepcopy__(self, memo):
        return self

    def reset(self):
        self.outbox = []
        self._inbox = []
        self.status = ''
        self.memory = {}

    def send(self, message):
        """
        Send a message to nodes listed in message's destination field.

        Note: Destination should be a list of nodes or one node.

        Update message's source field and  inserts in node's outbox one copy
        of it for each destination.

        """
        message.source = self
        message.destination = isinstance(message.destination, collections.Iterable) and \
                              message.destination or [message.destination]
        for destination in message.destination:
            logger.debug('Node %d sent message %s.' %
                         (self.id, message.__repr__()))
            m = message.copy()
            m.destination = destination
            self.outbox.insert(0, m)

    def receive(self):
        """
        Pop message from inbox but only if it has been there at least one step.

        Messages should be delayed for one step for visualization purposes.
        Messages are processed without delay only if they are pushed into empty
        inbox. So if inbox is empty when push_to_inbox is called _inboxDelay is
        set to True.

        This method is used only internally and is not supposed to be used
        inside algorithms.

        """
        if self._inbox and not self._inboxDelay:
            message = self._inbox.pop()
            logger.debug('Node %d received message %s' %
                         (self.id, message.__repr__()))
        else:
            message = None
        self._inboxDelay = False
        return message

    @property
    def inbox(self):
        return self._inbox

    def push_to_inbox(self, message):
        # TODO: for optimization remove _inboxDelay when not visualizing
        self._inboxDelay = self._inboxDelay or not self._inbox
        self._inbox.insert(0, message)

    @property
    def compositeSensor(self):
        return self._compositeSensor

    @compositeSensor.setter
    def compositeSensor(self, compositeSensor):
        self._compositeSensor = CompositeSensor(self, compositeSensor)

    @property
    def sensors(self):
        return self._compositeSensor.sensors

    @sensors.setter
    def sensors(self, sensors):
        self._compositeSensor = CompositeSensor(self, sensors)

    @property
    def commRange(self):
        return self._commRange

    @commRange.setter
    def commRange(self, commRange):
        self._commRange = commRange
        if self.network:
            self.network.recalculate_edges([self])

    def get_log(self):
        """ Special field in memory used to log messages from algorithms. """
        if not 'log' in self.memory:
            self.memory['log'] = []
        return self.memory['log']

    def log(self, message, level=logging.WARNING):
        """ Insert a log message in node memory. """
        assert isinstance(message, str)
        context = {
                   'algorithm': str(self.network.get_current_algorithm()),
                   'algorithmState': self.network.algorithmState,
                   }
        if not 'log' in self.memory:
            self.memory['log'] = [(level, message, context)]
        else:
            self.memory['log'].append((level, message, context))

    def get_dic(self):
        return {'1. info': {'id': self.id,
                    'status': self.status,
                    'position': self.network.pos[self],
                    'orientation': self.network.ori[self]},
                '2. communication': {'range': self.commRange,
                                     'inbox': self.box_as_dic('inbox'),
                                     'outbox': self.box_as_dic('outbox')},
                '3. memory': self.memory,
                '4. sensors': {sensor.name(): '%s(%.3f)' %
                                (sensor.probabilityFunction.name,
                                 sensor.probabilityFunction.scale)
                                 if hasattr(sensor, 'probabilityFunction') and
                                    sensor.probabilityFunction is not None
                                 else ('', 0)
                              for sensor in self.compositeSensor.sensors}}

    def box_as_dic(self, box):
        messagebox = self.__getattribute__(box)
        dic = {}
        for i, message in enumerate(messagebox):
            dic.update({'%d. Message' % (i + 1,): {'1 header': message.header,
                                          '2 source': message.source,
                                          '3 destination': message.destination,
                                          '4 data': message.data}})
        return dic
