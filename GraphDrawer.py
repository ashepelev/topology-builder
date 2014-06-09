__author__ = 'ash'

import networkx as nx
import matplotlib.pyplot as plt
from sets import Set
import Node
from Node import Switch
from Node import Router
from Node import ComputeNode
from Node import CloudController
import random
import Edge

class GraphDrawer:

    def __init__(self, node_list, edges_list):
        self.nodes = node_list
        self.edges = edges_list

    def get_edges(self):
        edges = []
        for edge in self.edges:
            edges.append(edge.node_pair)
        return edges

    def get_labels(self):
        labels = {}
        i = 0
        for node in self.nodes:
            try:
                labels[i] = node.hostname
            except AttributeError:
                labels[i] = "Switch id " + str(node.id)
            i += 1
        return labels

    def draw_graph(self, graph, labels=None, graph_layout='shell',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif',draw_bandwidth='max'):

        # create networkx graph
        G=nx.Graph()

        # add edges
        for edge in graph:
            G.add_edge(edge[0], edge[1])

        # these are different layouts for the network you may try
        # spring seems to work best
        if graph_layout == 'spring':
            graph_pos=nx.spring_layout(G)
        elif graph_layout == 'spectral':
            graph_pos=nx.spectral_layout(G)
        elif graph_layout == 'random':
            graph_pos=nx.random_layout(G)
        else:
            graph_pos=nx.shell_layout(G)

        # draw graph
        nx.draw_networkx_nodes(G,graph_pos,node_size=node_size,
                               alpha=node_alpha, node_color=node_color)
        nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                               alpha=edge_alpha,edge_color=edge_color)
        nx.draw_networkx_labels(G, graph_pos,labels,font_size=node_text_size,
                                font_family=text_font)

    #    if labels is None:
     #       labels = range(len(graph))

        edge_labels = []
        if draw_bandwidth == 'max':
            for edge in self.edges:
                edge_labels.append(edge.maxb)
        elif draw_bandwidth == 'avg':
            for edge in self.edges:
                edge_labels.append(edge.avg_bandw)
        else:
            print "Wrong draw_bandwidth type param"

        edge_labels = dict(zip(graph, edge_labels))
        nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels,
                                     label_pos=edge_text_pos)

        # show graph
        plt.show()