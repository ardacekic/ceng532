from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel,FIFOBroadcastPerfectChannel,GenericChannelWithLoopback
import networkx as nx
import time
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel,FIFOBroadcastPerfectChannel,GenericChannelWithLoopback
from TouegsAlgorithm import TouegRoutingComponent as TG


class testfrederickson:
    """
    2 Test methodes are used in testing:

    1)a tree construction
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)
    G.add_edge(0, 1)
    G.add_edge(1, 3)
    G.add_edge(0, 3)
    G.add_edge(1, 2)
    G.add_edge(1, 4)
    G.add_edge(4, 5)   

    2) ring
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    G.add_edge(5, 0)   

    topo.construct_from_graph(G, FRA, GenericChannel)

    results:
    1) Tree
    BFS Completed Reverse ....
    Tree :  {1: {2: {}, 4: {5: {}}}, 3: {}}
    Exiting

    2) Ring
    BFS Completed Reverse ....
    Tree :  {1: {2: {3: {}}}, 5: {4: {}}}
    Exiting
    """
    
    G = nx.Graph()
    #G.add_node(0)
    #G.add_node(1)
    #G.add_node(2)

    #G.add_edge(0, 1)
    #G.add_edge(1, 2)
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    G.add_edge(5, 0)   

    topo = Topology()

    topo.construct_from_graph(G, TG, GenericChannel)
    time.sleep(1)
    topo.start()
    time.sleep(10)
    topo.exit()
    
def main():    
    model = testfrederickson()

if __name__ == "__main__":
  main()