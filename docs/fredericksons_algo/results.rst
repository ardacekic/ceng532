.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The implementation of the Simple Frederickson's algorithm was carried out in the AHCv2 Python environment. Testing was conducted on various topologies, including ring and mesh topologies, to assess the algorithm's effectiveness. The primary objective of the algorithm is to function across all kinds of topologies. Frederickson's distributed BFS algorithm is well-suited for this purpose, as it efficiently finds the minimum path to any node, a critical feature in graph networks. Before delving into the implementation details, consider a ring topology where each node has two communication interfaces: one with the preceding node and another with the following node. This algorithm enables faster communication between nodes compared to the basic method of "passing the message to the right/left peer" because each node understands the path to a different node and how to transmit the information. Detailed and graphical results will be presented in the Results section. The research was conducted by reviewing papers on this algorithm, and the pseudocodes are provided in Section 1.3, "Distributed Algorithm." We employed the same coding scheme to implement the distributed algorithm in the AHCv2 environment.

.. figure:: figures/algo.jpg
  :width: 100
  
  The Frederickson's Algorithm Methodology

1. Explore Messages:
When an ⟨explore,f⟩ message arrives at some node u for the first time (i.e. when levelu = inf), node u is discovered by v and will be added to the subtree of v. Node v becomes the parent of u and the level of u (the depth of u in the BFS tree) is bound to f. To let v know that u has become its child, u sends back a reply ⟨reverse, true⟩

2. Forward Messages:
⟨forward,f⟩ messages are used to let the front nodes know they must send ⟨explore, f + 1⟩ messages to their unknown neighbors. If a node u at levelu < f receives such a ⟨forward, f ⟩ message, it forwards it to each child

3. Reverse Messages:
If a ⟨reverse, true⟩ message arrives at u it is certain that v is a child of u since the two cases in which such a message can arrive are:
first,v is just discovered by u, and thus becomes its child
second,v just discovered a new node in its subtree, and reports this back to its
parent u, so v is already a child of u.
In any case, we add v to the set of children of u (again) and we set bvalueu to true, to store that a ⟨reverse, true⟩ arrived.

.. figure:: figures/example_run.jpg
  :width: 250
  
  Example Run for (forward,2) Message

There are two issues in the implementation that could be addressed in future work. The first issue is the "old parent" problem, and the second is the omission of peer messaging in the implementation. Starting with the issue of missing peer messaging, when we investigate further "example run", it is evident that there is no response to a peer's explore message because the peer nodes are on the same level. According to the implementation described in the paper, communicating with peers is deemed unnecessary. The advanced Frederickson's algorithm addresses this issue by defining a new message type that allows nodes to also keep track of their connected peers. In the current implementation, all components are "logically" considered connected either up or down. The algorithm determines whether a connection is considered up or down based on which message is received first by a node. Addressing peer connections could be a focus for future work. It's important to note that in the topologies, nodes are not connected as peers; there is always a connector acting as a messaging bus.

Regarding the "old parent" problem, an error condition is visible in the provided figure 3 "The Old Parent Problem" . However, this issue will not occur in the AHCv2 environment because the propagation delay of all channels and connectors is the same, allowing messages to be heard simultaneously in simulations. Although this is not a problem in the simulated environment, it could be an issue in real-world applications where the algorithm might not perform correctly. To resolve this, new message types could be introduced as suggested in the paper, adding parent node information to explore messages to rectify the issue. While this solution is not yet implemented, it presents a potential area for future development.

.. figure:: figures/oldparent.jpg
  :width: 250
  
  The Old Parent Problem


Results
~~~~~~~~


In the AHCv2 environment, we have implemented two distinct network topologies: a ring topology and a random graph topology. Illustrations of these topologies and their connections are displayed in Figures 4 and 5. Additionally, details about the implementation messages for both topologies are included in the index for easy reference.

1. Ring topology result:

  Examining the figure titled "Ring Topology and Resulting BFS Tree," we observe the BFS tree with the initiator node labeled as zero. The levels of the tree are visible, and notably, node 3 could belong either to the branch linking nodes 1 and 2 or to the branch from nodes 0 through 5 to 4. This placement is determined by the algorithm, where the node that sends the explore message first gains the children. However, this assignment can vary with each simulation run. The implementation generates a message that is subsequently broadcast across the network as follows:
 1. BFS Completed Reverse ....
 2. Tree :  {1: {2: {3: {}}}, 5: {4: {}}}
 3. Exiting 

.. figure:: figures/ring_topo.png
  :width: 250
  
  Ring Topology and Resulting BFS Tree

2. Random graph topology result:

  Upon reviewing the figure titled "Random Topology and Resulting BFS Tree," we observe the BFS tree with the initiator node also set to zero. In this scenario, the structure of the BFS tree remains consistent, and the algorithm consistently produces the same result, provided all nodes in the network are functional. It should be noted that the algorithm does not verify whether the nodes are active or not:
 1. BFS Completed Reverse ....
 2.  Tree :  {1: {2: {}, 4: {5: {}}}, 3: {}}
 3.  Exiting

.. figure:: figures/grap_random.png
  :width: 250
  
  Random Topology and Resulting BFS Tree


The results from the random graph can be extrapolated to the mesh topology. The algorithm performs as expected, and from the zeroth node's perspective, the BFS tree is successfully generated and disseminated across the network.

Graphical analyses show that a minimum spanning tree (MST) is also formed, enabling the zeroth node to send messages efficiently to any other node. A key element in distributed networks is messaging complexity, which quantifies the total number of messages the algorithm needs to stabilize and reach a conclusion. The messaging complexity is capped at O(V^2), where V represents the number of nodes. Notably, this complexity remains consistent regardless of changes in topology, unless the nodes are interconnected as peers, which would suggest potential flaws in the algorithm’s design.

Discussion
~~~~~~~~~~

After implementing this algorithm, we gained several crucial insights about distributed networks, including BFS and MST on these networks.

Firstly, creating an MST is crucial for efficiently delivering messages to nodes. Secondly, it's important to acknowledge that distributed networks may not always exhibit predictable behavior. The implemented code must accommodate all edge cases. In this context, propagation delay poses a significant challenge. We did not devise a solution for this within the AHCv2 environment, as it does not present this issue due to uniform message passing times across channels. However, the old-parent problem remains a significant concern in real-life applications. We have outlined potential future work on this topic in the Implementation and Methodology section.

In conclusion, we can identify two potential future developments for Frederickson's algorithm implementation:

1. Introducing new message types to address the old parent problem.
2. Implementing a mechanism to handle peer connections.
 
