import csv
import os
import random
import sys
import time
from threading import Lock, Condition

sys.path.insert(0, os.getcwd())

import networkx as nx

from adhoccomputing.Generics import *
from adhoccomputing.GenericModel import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

from chandymisra import CMNode, CMLayer

WAIT_FINISH_TIMEOUT = 100 # seconds

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

def add_random_weights(G: nx.Graph, min: int, max: int):
    for u, v in G.edges():
        weight = random.randint(min, max)
        G[u][v]['weight'] = weight

def test_dense_gnm_random_graph(n, m, weight_min, weight_max, seed=None):
    # n = 2
    # G = nx.connected_watts_strogatz_graph(n, 4, 0.10)
    # G = nx.generators.karate_club_graph()
    # G = nx.generators.social.les_miserables_graph()
    # G = make_graph()
    G = nx.generators.dense_gnm_random_graph(n, m, seed)
    # Add random weights
    add_random_weights(G, weight_min, weight_max)
    # visualize_graph(G)
    topo = Topology()
    topo.construct_from_graph(G, CMNode, GenericChannel)
    wait_finish_lock = Lock()
    wait_finish_cv = Condition(wait_finish_lock)
    algorithm_duration = -1
    # On finish handler
    def on_finish(duration: float):
        nonlocal algorithm_duration
        algorithm_duration = duration
        with wait_finish_cv:
            wait_finish_cv.notify()
    # Initialize all nodes including dest node
    dest_node: CMNode = topo.get_random_node()
    for n in topo.nodes.values():
        n: CMNode
        n.initialize_subcomponents(n == dest_node, dest_node.componentinstancenumber, on_finish)
    topo.start()
    with wait_finish_cv:
        if not wait_finish_cv.wait(WAIT_FINISH_TIMEOUT):
            logger.error(f"Unable to finish the graph withing {WAIT_FINISH_TIMEOUT} seconds.")
    # Send exit event
    topo.exit()
    print(show_predecessors())
    print(f"dest node idx: {dest_node.componentinstancenumber}")
    return algorithm_duration
    # Send a mock message
    # rand_node: CMNode = topo.get_random_node()
    # rand_node.applicationlayer.send_down(Event(None, EventTypes.MFRT, "test"))

def main():
    all_dur = []
    for i in range(100, 505, 5):
        nodes, edges = i, 505*5
        dur = test_dense_gnm_random_graph(nodes, edges, 1, 10)
        if dur == -1:
            # Timeout, break because next tests are likely to have timeouts
            break
        all_dur.append((nodes, edges, dur))
        print(f"Nodes: {nodes} Edges: {edges} Duration: {dur}")
    time.sleep(2)
    print(all_dur)

if __name__ == "__main__":
    main()