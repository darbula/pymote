from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class YoYo(NodeAlgorithm):
    default_params = {'neighborsKey': 'Neighbors',
                      'inNeighborsKey': 'InNeighbors',
                      'outNeighborsKey': 'OutNeighbors'}

    # Store assigned id (assigned in SetupYoYo)
    ID_KEY = 'id'

    # Store received ids, I'll use a dict {id_value: [source_nodes]}
    RECEIVED_IDS_KEY = 'received_ids'

    # Store received ids that were received while waiting for responses,
    # I'll use a dict {id_value: [source_nodes]}
    RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY = 'received_ids_while_waiting'

    # Store received responses, 
    # I'll use a dict {response_value: [source_nodes]}
    RECEIVED_RESPONSES_KEY = 'received_responses'

    # Store nodes that requested pruning, list [source_nodes]
    REQUESTED_PRUNING_KEY = 'requested_pruning'

    # Store number of sent ids
    SENT_IDS_KEY = 'sent_ids'

    # This is sent when a PRUNE is requested
    PRUNE_REQUEST = 'prune'

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.inNeighborsKey] = []
            node.memory[self.outNeighborsKey] = []

            node.memory[self.neighborsKey] = \
                node.compositeSensor.read()['Neighbors']
            node.status = 'INITIATOR'

            node.memory[self.RECEIVED_IDS_KEY] = {}
            node.memory[self.RECEIVED_RESPONSES_KEY] = {}
            node.memory[self.REQUESTED_PRUNING_KEY] = []
            node.memory[self.SENT_IDS_KEY] = 0
            node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY] = {}

            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,
                                       destination=node))

    def invert_edges(self, node, nodes_to_process, invert_from):
        for node_to_process in nodes_to_process:
            if invert_from == 'outNeighbors':
                node.memory[self.outNeighborsKey].remove(node_to_process)
                node.memory[self.inNeighborsKey].append(node_to_process)
            elif invert_from == 'inNeighbors':
                node.memory[self.inNeighborsKey].remove(node_to_process)
                node.memory[self.outNeighborsKey].append(node_to_process)

    def prune_nodes(self, node, nodes_to_process, prune_from):
        for node_to_process in nodes_to_process:
            if prune_from == 'outNeighbors':
                node.memory[self.outNeighborsKey].remove(node_to_process)
            elif prune_from == 'inNeighbors':
                node.memory[self.inNeighborsKey].remove(node_to_process)

    def send_responses(self, node, no_received=False):
        # Find min id
        min_id = min(node.memory[self.RECEIVED_IDS_KEY])
        no_nodes = []
        prune_nodes = []

        received_ids = node.memory[self.RECEIVED_IDS_KEY]
        for received_id in received_ids:
            if no_received:
                # Send NO to all node that sent an id
                node.send(
                    Message(destination=received_ids[received_id],
                            header='response',
                            data=(False, ))
                )
                no_nodes.extend(received_ids[received_id])

            elif received_id == min_id:
                # Send YES responses to all inNeighbors that send min_id

                if len(received_ids) == 1 and \
                        len(node.memory[self.outNeighborsKey]) == 0:
                    # If node received only min_id and has no outNeighbors
                    # remaining after inverting and pruning
                    # it will become a LEAF SINK,
                    # so send a PRUNE request with the YES response as well
                    node.send(
                        Message(destination=received_ids[received_id][0],
                                header='response',
                                data=(True, self.PRUNE_REQUEST))
                    )
                    prune_nodes.append(received_ids[received_id][0])
                else:
                    node.send(
                        Message(destination=received_ids[received_id][0],
                                header='response',
                                data=(True, ))
                    )

                # Send PRUNE request to extra nodes that sent min_id
                # and add them to prune_nodes to be pruned
                node.send(
                    Message(destination=received_ids[received_id][1:],
                            header='response',
                            data=(True, self.PRUNE_REQUEST))
                )
                prune_nodes.extend(received_ids[received_id][1:])

            else:
                # Send NO responses to all inNeighbors that didn't
                # send min_id and add them to no_nodes to be inverted
                node.send(
                    Message(destination=received_ids[received_id],
                            header='response',
                            data=(False, ))
                )
                no_nodes.extend(received_ids[received_id])

        return no_nodes, prune_nodes

    def change_status(self, node):

        if node.status == 'SOURCE':
            if len(node.memory[self.inNeighborsKey]) == 0:
                if len(node.memory[self.outNeighborsKey]) == 0:
                    node.status = 'LEADER'
            else:
                if len(node.memory[self.outNeighborsKey]) > 0:
                    node.status = 'INTERMEDIATE'
                else:
                    node.status = 'SINK'

        elif node.status == 'INTERMEDIATE':
            if len(node.memory[self.outNeighborsKey]) == 0:
                if len(node.memory[self.inNeighborsKey]) == 0:
                    node.status = 'PRUNED'

        elif node.status == 'SINK':
            if len(node.memory[self.inNeighborsKey]) == 0:
                node.status = 'PRUNED'
            else:
                node.status = 'INTERMEDIATE'

        elif node.status == 'IDLE':
            if node.memory[self.inNeighborsKey]:
                node.status = 'SINK'
                if node.memory[self.outNeighborsKey]:
                    node.status = 'INTERMEDIATE'
            else:
                node.status = 'SOURCE'

        self.do(node)

    def receive_id(self, node, message):
        if node.memory[self.SENT_IDS_KEY]:
            ids = node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY]

            if message.data in ids:
                ids[message.data].append(message.source)
            else:
                ids[message.data] = [message.source]
        else:
            ids = node.memory[self.RECEIVED_IDS_KEY]

            if message.data in ids:
                ids[message.data].append(message.source)
            else:
                ids[message.data] = [message.source]

    def receive_response(self, node, message):
        responses = node.memory[self.RECEIVED_RESPONSES_KEY]
        response = message.data[0]

        if response in responses:
            responses[response].append(message.source)
        else:
            responses[response] = [message.source]

        if self.PRUNE_REQUEST in message.data:
            node.memory[self.REQUESTED_PRUNING_KEY].append(message.source)

    def do_source(self, node):
        if node.memory[self.SENT_IDS_KEY] == 0:
            node.memory[self.RECEIVED_RESPONSES_KEY] = {}
            node.memory[self.REQUESTED_PRUNING_KEY] = []

            node.send(Message(destination=node.memory[self.outNeighborsKey],
                              header='id',
                              data=node.id))

            node.memory[self.SENT_IDS_KEY] = \
                len(node.memory[self.outNeighborsKey])

        else:
            responses = node.memory[self.RECEIVED_RESPONSES_KEY]

            # If responses received for all sent ids handle them
            num_of_responses = sum(
                [len(sources) for sources in responses.values()]
            )

            if num_of_responses >= node.memory[self.SENT_IDS_KEY]:

                if False in responses:
                    nodes_to_invert = responses[False]
                else:
                    nodes_to_invert = []

                nodes_to_prune = node.memory[self.REQUESTED_PRUNING_KEY]

                # Invert edges
                self.invert_edges(node, nodes_to_invert, 'outNeighbors')

                # Prune nodes
                self.prune_nodes(node, nodes_to_prune, 'outNeighbors')

                node.memory[self.RECEIVED_RESPONSES_KEY] = {}
                node.memory[self.REQUESTED_PRUNING_KEY] = []
                node.memory[self.SENT_IDS_KEY] = 0
                node.memory[self.RECEIVED_IDS_KEY] = \
                    node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY]
                node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY] = {}

                # End iteration and change status if needed
                self.change_status(node)

    def do_intermediate(self, node):
        if node.memory[self.SENT_IDS_KEY] == 0:

            ids = node.memory[self.RECEIVED_IDS_KEY]

            # If ids received from all inNeighbors handle them
            num_of_ids = sum([len(sources) for sources in ids.values()])

            if num_of_ids >= len(node.memory[self.inNeighborsKey]):
                node.memory[self.RECEIVED_RESPONSES_KEY] = {}
                node.memory[self.REQUESTED_PRUNING_KEY] = []

                # Find min id
                min_id = min(ids)

                # Forward min id to outNeighbors
                node.send(
                    Message(destination=node.memory[self.outNeighborsKey],
                            header='id',
                            data=min_id)
                )

                node.memory[self.SENT_IDS_KEY] = \
                    len(node.memory[self.outNeighborsKey])

        else:
            responses = node.memory[self.RECEIVED_RESPONSES_KEY]

            # If responses received for all sent ids handle them
            num_of_responses = sum(
                [len(sources) for sources in responses.values()]
            )

            if num_of_responses >= node.memory[self.SENT_IDS_KEY]:
                if False in responses:
                    nodes_to_invert = responses[False]
                    no_received = True
                else:
                    nodes_to_invert = []
                    no_received = False

                nodes_to_prune = node.memory[self.REQUESTED_PRUNING_KEY]

                # Invert edges
                self.invert_edges(node, nodes_to_invert, 'outNeighbors')

                # Prune nodes
                self.prune_nodes(node, nodes_to_prune, 'outNeighbors')

                # Add edges to invert from NO responses sent
                # Add nodes to prune from PRUNE requests sent
                no_response_nodes, prune_nodes = \
                    self.send_responses(node, no_received=no_received)

                # Invert edges
                self.invert_edges(node, no_response_nodes, 'inNeighbors')

                # Prune nodes
                self.prune_nodes(node, prune_nodes, 'inNeighbors')

                node.memory[self.RECEIVED_RESPONSES_KEY] = {}
                node.memory[self.REQUESTED_PRUNING_KEY] = []
                node.memory[self.RECEIVED_IDS_KEY] = \
                    node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY]
                node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY] = {}
                node.memory[self.SENT_IDS_KEY] = 0

                # End iteration and change status if needed
                self.change_status(node)

    def do_sink(self, node):
        ids = node.memory[self.RECEIVED_IDS_KEY]

        # If ids received from all inNeighbors handle them
        num_of_ids = sum([len(sources) for sources in ids.values()])

        if num_of_ids >= len(node.memory[self.inNeighborsKey]):
            no_response_nodes, prune_nodes = self.send_responses(node)

            # Invert edges
            self.invert_edges(node, no_response_nodes, 'inNeighbors')

            # Prune nodes
            self.prune_nodes(node, prune_nodes, 'inNeighbors')

            node.memory[self.RECEIVED_IDS_KEY] = \
                node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY]
            node.memory[self.RECEIVED_IDS_WHILE_WAITING_RESPONSE_KEY] = {}
            node.memory[self.SENT_IDS_KEY] = 0

            # End iteration and change status if needed
            self.change_status(node)

    def do(self, node):
        if node.status == 'SOURCE':
            self.do_source(node)
        elif node.status == 'INTERMEDIATE':
            self.do_intermediate(node)
        elif node.status == 'SINK':
            self.do_sink(node)

    def initiator(self, node, message):
        if message.header == NodeAlgorithm.INI:
            # Special case. Only one node in graph
            # If node has no neighbors set its status to LEADER
            if not node.memory[self.neighborsKey]:
                node.status = 'LEADER'
                return

            # default destination: send to every neighbor
            node.send(Message(header='init_id', data=node.id))

            node.status = 'IDLE'

    def idle(self, node, message):
        if message.header == 'init_id':
            if message.data < node.id:
                node.memory[self.inNeighborsKey].append(message.source)
            else:
                node.memory[self.outNeighborsKey].append(message.source)

            num_of_in_neighbors = len(node.memory[self.inNeighborsKey])
            num_of_out_neighbors = len(node.memory[self.outNeighborsKey])

            if num_of_in_neighbors + num_of_out_neighbors >= \
                    len(node.memory[self.neighborsKey]):
                self.change_status(node)

        elif message.header == 'id':
            self.receive_id(node, message)

    def source(self, node, message):
        if message.header == 'response':
            num_receiverd_responses = self.receive_response(node, message)

        elif message.header == 'id':
            num_received_ids = self.receive_id(node, message)

        self.do_source(node)

    def intermediate(self, node, message):
        if message.header == 'id':
            self.receive_id(node, message)

        elif message.header == 'response':
            self.receive_response(node, message)

        self.do_intermediate(node)

    def sink(self, node, message):
        if message.header == 'id':
            self.receive_id(node, message)

        elif message.header == 'response':
            self.receive_response(node, message)

        self.do_sink(node)

    def pruned(self, node, message):
        pass

    def leader(self, node, message):
        pass

    STATUS = {
        'INITIATOR': initiator,
        'IDLE': idle,
        'SOURCE': source,
        'INTERMEDIATE': intermediate,
        'SINK': sink,
        'PRUNED': pruned,
        'LEADER': leader
    }