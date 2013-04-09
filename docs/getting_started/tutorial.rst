Introductory Tutorial
#####################

This tutorial assumes that the pymote and all required packages are installed.
If not, please refer to the :doc:`installation` section of this documentation.

Create network::

    net_gen = NetworkGenerator(100)
    net = net_gen.generate_random_network()

Import algorithm::

    from pymote.algorithms.broadcast import Flood
    net.algorithms = ((Flood,{'informationKey':'I'}),)
    net.algorithms

Run simulation::

    sim = Simulation(net)
    sim.run()

Check results::

    for n in net.nodes():
        print n.memory


Add nodes

Set up environment

Add sensors

Config

Start gui inspection

Create simple algorithm

Simulate through console

Simulate trough gui


.. TODO:: Write tutorial