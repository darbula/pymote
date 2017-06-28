from pymote import NetworkGenerator, Simulation, write_pickle, Network
from pymote.algorithms.santoro2007.yoyo import YoYo


class TestSantoro2007(unittest.TestCase):

    def do_test(self, net, name):
        net.algorithms = (YoYo, )
        sim = Simulation(net, logLevel='WARNING')
        sim.run()

        min_id = min(sim.network.nodes(), key=lambda node: node.id).id
        for node in sim.network.nodes():
            if node.id == min_id:
                # Check if the node with the smallest ID is the LEADER
                assert node.status == 'LEADER', \
                    '%s: Node %d has status %s, not LEADER' % \
                    (name, node.id, node.status)
            else:
                # Check if every other node is PRUNED
                assert node.status == 'PRUNED', \
                    '%s: Node %d has status %s, not PRUNED' % \
                    (name, node.id, node.status)

    def test_santoro2007(self):
        N_ITERS = 5
        N_NETWORKS = 15
        N_NODES_STEP = 5

        node_range = 100
        nets = [
            [(100, 100)],
            [(100, 100), (175, 250), (250, 175), (100, 250),
                (175, 175), (100, 175)],
            [(100, 100), (150, 200), (175, 175), (175, 100),
                (250, 175), (250, 250), (325, 250), (325, 325), (325, 400)]
        ]

        for i, node_positions in enumerate(nets, start=1):
            net = Network()
            for node_pos, name in node_positions:
                net.add_node(pos=node_pos, commRange=node_range)

            self.do_test(net, 'Special %d' % i)

        for i in range(N_ITERS):
            for n_nodes in range(N_NODES_STEP,
                                 N_NETWORKS*N_NODES_STEP+N_NODES_STEP,
                                 N_NODES_STEP):

                net_gen = NetworkGenerator(n_nodes)
                net = net_gen.generate_random_network()
                self.do_test(net, 'Random %d, %d nodes' % (i, n_nodes))
