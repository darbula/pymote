Pymote
======
Pymote is a high level Python library for event based simulation and evaluation of distributed algorithms.


Installation
------------
To install run::

    pip install pymote

Requirements:
    networkx
    numpy
    scipy
    pypng
    ipython
    matplotlib

Quick overview
--------------
If you haven't already import pymote::
    
    from pymote import *

Network is basic component and you can make it by instantiation of Network class::

    net = Network()

and by adding some nodes::

net.add_node()