from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class DFT(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = \
                node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(
            header=NodeAlgorithm.INI,
            destination=ini_node
        ))

    def initiator(self, node, message):
        if message.header == NodeAlgorithm.INI:
            node.memory["parent"] = None
            node.memory["unvisited"] = list(node.memory[self.neighborsKey])
            self.visit(node)
        else:
            raise Exception("Dont disturb intiator!")

    def idle(self, node, message):
        if message.header == 'Token':
            node.memory["parent"] = message.source
            node.memory["unvisited"] = list(node.memory[self.neighborsKey])
            node.memory["unvisited"].remove(node.memory["parent"])
            self.visit(node)
        else:
            raise Exception("Should not be here.")

    def visited(self, node, message):
        if message.header == 'Token':
            node.memory["unvisited"].remove(message.source)
            node.send(Message(header='Backedge',
                              destination=message.source))
        elif message.header == 'Return':
            self.visit(node)
        elif message.header == 'Backedge':
            self.visit(node)

    def done(self, node, message):
        raise Exception("I'm done!")

    def visit(self, node):
        if len(node.memory["unvisited"]) == 0:
            if node.memory["parent"] is not None:
                node.send(Message(
                    header='Return',
                    destination=node.memory["parent"]
                ))
            node.status = "DONE"
        else:
            next_unvisited = node.memory["unvisited"].pop()
            node.send(Message(header='Token',
                              destination=next_unvisited))
            node.status = "VISITED"

    STATUS = {
        'INITIATOR': initiator,
        'IDLE': idle,
        'VISITED': visited,
        'DONE': done,
    }


class DFStar(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = \
                node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(
            header=NodeAlgorithm.INI,
            destination=ini_node
        ))

    def initiator(self, node, message):
        if message.header == NodeAlgorithm.INI:
            node.memory['initiator'] = True
            node.memory['unvisited'] = list(node.memory[self.neighborsKey])
            node.memory['next'] = node.memory['unvisited'].pop()
            if (node.memory['unvisited']):
                node.send(Message(
                    header='T',
                    destination=node.memory['next']
                ))
                node.send(Message(
                    header='Visited',
                    destination=node.memory['unvisited']
                ))
                node.status = 'VISITED'
            else:
                node.status = 'DONE'

    def idle(self, node, message):
        if message.header == 'T':
            node.memory['unvisited'] = list(node.memory[self.neighborsKey])
            self.first_visit(node, message)

        if message.header == 'Visited':
            node.memory['unvisited'] = list(node.memory[self.neighborsKey])
            node.memory['unvisited'].remove(message.source)
            node.status = 'AVAILABLE'

    def available(self, node, message):
        if message.header == 'T':
            self.first_visit(node, message)

        if message.header == 'Visited':
            node.memory['unvisited'].remove(message.source)

    def visited(self, node, message):
        if message.header == 'T':
            node.memory['unvisited'].remove(message.source)
            # late visited, should not happen in unitary communication delay
            if node.memory['next'] == message.source:
                self.visit(node, message)

        if message.header == 'Visited':
            node.memory['unvisited'].remove(message.source)
            if node.memory['next'] == message.source:
                self.visit(node, message)

        if message.header == 'Return':
            self.visit(node, message)

    def done(self, node, message):
        pass

    def first_visit(self, node, message):
        # TODO: initiator is redundant - it can be deduced from entry==None
        node.memory['initiator'] = False
        node.memory['entry'] = message.source
        try:
            node.memory['unvisited'].remove(message.source)
        except ValueError:
            pass
        if (node.memory['unvisited']):
            node.memory['next'] = node.memory['unvisited'].pop()
            node.send(Message(
                header='T',
                destination=node.memory['next']
            ))
            node.send(Message(
                header='Visited',
                destination=(set(node.memory[self.neighborsKey]) -
                             set([node.memory['entry'], node.memory['next']]))
                ))
            node.status = 'VISITED'
        else:
            node.send(Message(
                header='Return',
                destination=node.memory['entry']))
            node.send(Message(
                header='Visited',
                destination=(set(node.memory[self.neighborsKey]) -
                             set([node.memory['entry']]))
                ))
            node.status = 'DONE'

    def visit(self, node, message):
        if (node.memory['unvisited']):
            node.memory['next'] = node.memory['unvisited'].pop()
            node.send(Message(
                header='T',
                destination=node.memory['next']
            ))
        else:
            if not node.memory['initiator']:
                node.send(Message(
                    header='Return',
                    destination=node.memory['entry']
                ))
            node.status = 'DONE'

    STATUS = {
        'INITIATOR': initiator,
        'IDLE': idle,
        'AVAILABLE': available,
        'VISITED': visited,
        'DONE': done,
    }
