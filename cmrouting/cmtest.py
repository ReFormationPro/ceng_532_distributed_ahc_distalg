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

def show_predecessors():
    predecessors = {}
    for l in CMLayer.LAYERS:
        l: CMLayer
        predecessors[l.componentinstancenumber] = l.predecessor_instance_number
    return predecessors

def make_graph():
    G = nx.Graph()

    G.add_edge("a", "b", weight=0.6)
    G.add_edge("a", "c", weight=0.2)
    G.add_edge("c", "d", weight=0.1)
    G.add_edge("c", "e", weight=0.7)
    G.add_edge("c", "f", weight=0.9)
    G.add_edge("a", "d", weight=0.3)
    return G

def visualize_graph(G, figure_name="graph.jpg"):
    import matplotlib.pyplot as plt

    pos = nx.spring_layout(G)  # Compute node positions
    nx.draw(G, pos)
    node_labels = {node: str(node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_color='black', verticalalignment='center', horizontalalignment='center')
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.savefig(figure_name, format="jpg")
    plt.show()

def main():
    # n = 2
    # G = nx.connected_watts_strogatz_graph(n, 4, 0.10)
    G = nx.generators.karate_club_graph()
    # G = nx.generators.social.les_miserables_graph()
    # G = make_graph()
    visualize_graph(G)
    topo = Topology()
    topo.construct_from_graph(G, CMNode, GenericChannel)
    # Initialize all nodes including dest node
    dest_node: CMNode = topo.get_random_node()
    for n in topo.nodes.values():
        n: CMNode
        n.initialize_subcomponents(n == dest_node)
        #n.initialize_subcomponents(n.componentinstancenumber == dest_node.componentinstancenumber)
        #n.initialize_subcomponents(n.componentinstancenumber == "f")
    topo.start()
    time.sleep(30)
    print(show_predecessors())
    print(f"dest node idx: {dest_node.componentinstancenumber}")
    # Send a mock message
    # rand_node: CMNode = topo.get_random_node()
    # rand_node.applicationlayer.send_down(Event(None, EventTypes.MFRT, "test"))
    time.sleep(2)


if __name__ == "__main__":
    main()