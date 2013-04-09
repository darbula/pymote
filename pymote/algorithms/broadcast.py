from pymote.algorithm import NodeAlgorithm
from pymote.message import Message



class Flood(NodeAlgorithm):
    required_params = ('informationKey',)
    default_params = {'neighborsKey':'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0,Message(header=NodeAlgorithm.INI,
                                             destination=ini_node))

    def initiator(self, node, message):
        if message.header==NodeAlgorithm.INI:
            node.memory[self.informationKey] = message.data
            node.send(Message(header='Information',  # default destination: send to every neighbor
                              data=message.data))
        node.status = 'DONE'

    def idle(self, node, message):
        if message.header=='Information':
            node.memory[self.informationKey] = message.data
            destination_nodes = list(node.memory[self.neighborsKey])
            destination_nodes.remove(message.source) # send to every neighbor-sender
            if destination_nodes:
                node.send(Message(destination=destination_nodes,
                                  header='Information',
                                  data=message.data))
        node.status = 'DONE'

    def done(self, node, message):
        pass

    STATUS = {
              'INITIATOR': initiator,
              'IDLE': idle,
              'DONE': done,
             }