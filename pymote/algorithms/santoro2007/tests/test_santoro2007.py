from pymote import NetworkGenerator, Simulation, write_pickle, Network
from pymote.algorithms.santoro2007.yoyo import YoYo


def do_test(net):
    net.algorithms = (YoYo, )
    sim = Simulation(net, logLevel='WARNING')
    try:
        sim.run()
    except e:
        net.show()
        write_pickle(net, 'TestYoYo.npc.gz')
        print(e)
        raw_input('Showing graph plot, press ENTER to continue')
        exit()

    min_id = min(sim.network.nodes(),
                 key=lambda node: node.id).id
    for node in sim.network.nodes():
        try:
            if node.id == min_id:
                # Check if the node with the smallest ID is the LEADER
                assert node.status == 'LEADER', \
                    'Node %d has status %s, not LEADER' % \
                    (node.id, node.status)
            else:
                # Check if every other node is PRUNED
                assert node.status == 'PRUNED', \
                    'Node %d has status %s, not PRUNED' % \
                    (node.id, node.status)

        except AssertionError as e:
            net.show()
            write_pickle(net, 'TestYoYo.npc.gz')
            print(e)
            raw_input('Showing graph plot, press ENTER to continue')
            exit()

N_ITERS = 5
N_NETWORKS = 15
N_NODES_STEP = 5

print('Testing special cases')

node_range = 100
nets = [
    [(100, 100)],
    [(100, 100), (175, 250), (250, 175), (100, 250), (175, 175), (100, 175)],
    [(100, 100), (150, 200), (175, 175), (175, 100), (250, 175), (250, 250),
        (325, 250), (325, 325), (325, 400)]
]

for i, node_positions in enumerate(nets, start=1):
    net = Network()
    for node_pos in node_positions:
        net.add_node(pos=node_pos, commRange=node_range)

    do_test(net)
    print('Special case network %d PASS' % i)

print('Testing random networks')

for i in range(N_ITERS):
    for n_nodes in range(N_NODES_STEP,
                         N_NETWORKS*N_NODES_STEP+N_NODES_STEP,
                         N_NODES_STEP):

        net_gen = NetworkGenerator(n_nodes)
        net = net_gen.generate_random_network()
        do_test(net)
        print('Random network with %d nodes PASS' % n_nodes)
