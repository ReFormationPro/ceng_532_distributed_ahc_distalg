import csv
import os
import random
import sys
import time

sys.path.insert(0, os.getcwd())

import networkx as nx

from adhoccomputing.Generics import *
from adhoccomputing.GenericModel import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

from chandymisra import CMNode, CMLayer

def average(l):
    sum = 0
    for value in l:
        sum = sum + value

    return sum / len(l)

def make_graph():
    predecessors = {}
    for l in CMLayer.LAYERS:
        l: CMLayer
        predecessors[l.componentinstancenumber] = l.predecessor_instance_number
    return predecessors

def main():
    #n = 2
    #G = nx.connected_watts_strogatz_graph(n, 4, 0.10)
    G = nx.generators.karate_club_graph()
    topo = Topology()
    topo.construct_from_graph(G, CMNode, GenericChannel)
    # Initialize all nodes including dest node
    dest_node: CMNode = topo.get_random_node()
    for n in topo.nodes.values():
        n.initialize_subcomponents(n == dest_node)
    topo.start()
    time.sleep(3)
    print(make_graph())
    print(f"dest node idx: {dest_node.componentinstancenumber}")
    # Send a mock message
    # rand_node: CMNode = topo.get_random_node()
    # rand_node.applicationlayer.send_down(Event(None, EventTypes.MFRT, "test"))
    time.sleep(2)


if __name__ == "__main__":
    main()