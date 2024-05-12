.. include:: substitutions.rst

|fredericksons_algo|
=========================================

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In 1985, Greg N. Frederickson outlined a Breadth-First Search Tree Algorithm in his paper A Single Source Shortest Path Algorithm for a Planar Distributed Network, which served as a foundational component for creating an single-source shortest-path algorithm. However, the explanation of this BFS algorithm lacked comprehensive detail and operated under the assumption that messages within the algorithm were processed in a first-in-first-out (FIFO) manner.

In 2000, Tel reviewed and made modifications to Frederickson’s BFS algorithm. Despite this, Tel's notation of the algorithm remained incomplete and still relied on the assumption of a FIFO environment.

In 2006, Tel outlined a fix to address the shortcomings, but once again, the FIFO assumption persisted. Van Moolenbroek suggested an alternative fix in the same year, but no further research was conducted on the subject. 

The way the Frederickson's how to build the algorithm will be disscuessed in this paper and it will be implemented. The Tel's algorithm update is similar to advanced algorithm the Frederickson proposed.

Distributed Algorithm:  Frederickson's Algorithm 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Consider a scenario where data needs to traverse through various nodes within a network. An essential concern in distributed computing lies in efficiently directing this data flow, aiming to minimize the number of nodes or paths utilized while keeping costs at a minimum. To achieve this goal, it's imperative to employ algorithms capable of establishing the most optimal paths between network nodes. Once these optimal routes are established, data can seamlessly navigate through the network.

In order to route data through paths with the lowest costs, algorithms such as all-pairs shortest-path algorithms come into play. On the other hand, when the objective is to route data utilizing the minimum number of nodes, a breadth-first search (BFS) algorithm becomes instrumental.

Frederickson [1985] introduced a distributed BFS algorithm, which he leveraged for developing an all-pairs shortest-path algorithm. Frederickson's Distributed BFS Algorithm, also known as the Distributed Breadth-First Search Algorithm, is a parallel algorithm for traversing the network nodes.
The algorithm is designed to run on a distributed system, where each node in the graph is represented by a separate processor. The algorithm is based on the concept of breadth-first search, where the nodes are visited in a level-by-level manner.

1. **The algorithm has the following properties:** 
It is a parallel algorithm, which means it can be run on multiple processors simultaneously.
It is a distributed algorithm, which means each processor is responsible for a portion of the graph.
It is a breadth-first search algorithm, which means it visits nodes in a level-by-level manner.
It is a synchronous algorithm, which means all processors must reach the same state at the same time.

2. **The algorithm has several advantages over traditional breadth-first search algorithms:** 
It is more efficient than traditional BFS algorithms, as it can be run in parallel on multiple processors.
It is more scalable, as it can be run on large graphs with a large number of processors.
It is more robust, as it can handle graphs with cycles and disconnected components.

3. **The algorithm has some limitations:** 
It requires a large amount of communication between processors, which can be a bottleneck in large graphs.
It requires a synchronous communication model, which can be challenging to implement in practice.
It may not be suitable for graphs with a high degree of connectivity, as the communication overhead can become too large.

**How Algorithm Works & Pseudo Code:** 

Initial Configuration
---------------------

Nodes initiate the algorithm with several key variables:

- ``levelu``: Denotes the node's position in the BFS tree, initialized to infinity (∞) except for the initiator, which is set to 0.
- ``levelu[n]``: Records the levels of a node's neighbors, all initially set to infinity.
- ``parentu``: Identifies the node's parent in the BFS tree, initially undefined.
- ``Childu``: Contains the node's children in the tree, starting as an empty set.
- ``k``: The current round of the algorithm, with the initiator beginning at 0.
- ``bvalueu``: A boolean flag to indicate receipt of a "reverse true" message, initially set to false.
- ``expectedrepliesu[n]``: An array counting the expected replies from neighbors, initialized to 0 for all.

Execution Process
-----------------

The algorithm progresses in rounds, initiated by the starting node:

1. **Initiation Phase**: The initiator sets its level to zero, begins the first round by sending "explore k" messages to its neighbors, adding them to its ``Childu`` set, and awaiting a reply from each.

2. **Message Handling**:

   - **Forward Messages**: On receiving a "forward f" message, nodes compare their level to f. If less, they forward this message to their children. If equal, they send "explore f+1" messages to neighbors not at level f-1.

   - **Explore Messages**: Upon receiving an "explore f" message, actions vary:

     - If ``levelu`` is infinity, the node updates its parent to the sender, sets its level to f, and sends back a "reverse true".
     - If already at a defined level, the node updates its knowledge of the sender's level and responds with a "reverse false".

   - **Reverse Messages**: After sending out all messages, nodes await replies to determine if new nodes were added beneath them. This influences whether a "reverse true" or "reverse false" message is relayed upwards or, for the initiator, whether another round is initiated or the algorithm concludes.

.. _fredericksons_algo:

.. code-block:: RST
    :linenos:
    :caption: Frederickson's Distributed BFS Algorithm init() function.

    var
        level_u                    : integer init inf
        level_u[n]                 : integer init inf for each n in Neigh_u
        parent_u                   : process init undef
        Child_u                    : process init 0
        k                          : integer init zero
        bvalue_u                   : boolean init false
        expectedreplies_u[n]       : integer init zero for each n in Neigh_u

    For the initiator i only, execute once:
    begin
        level_i set 0
        k set 1
        for all n in Neigh_i, do
            Child_u ← Child_u u {n}
            send (explore, k) to n
            expectedreplies_i[n] set 1
    end

.. code-block:: RST
    :linenos:
    :caption: Frederickson's Distributed BFS Algorithm forward() function.

    For each process u, upon receipt of (forward, f) from v:
    begin
        bvalue_u set false
        forall n in Neigh_u: reply_u[n] set 0
        if level_u < f then
            forall c in Child_u do
                send (forward, f) to c
                reply_u[c] set reply_u[c] + 1
        if level_u = f then
            forall n in neigh_u where level_u[n] != f - 1 do
                send (explore, f + 1) to n
                expectedreplies_u[n] set expectedreplies_u[n] + 1
    end

.. code-block:: RST
    :linenos:
    :caption: Frederickson's Distributed BFS Algorithm explore() function.
    
    For each process u, upon receipt of (explore, f) from v:
    begin
        if level_u = inf then
            parent_u set v
            level_u set f
            send (reverse, true) to v
        else if level_u = f then
            level_u[v] set f - 1
            send (reverse, false) to v
        else if level_u = f - 1 then
            Interpret as (reverse, false) message
    end

.. code-block:: RST
    :linenos:
    :caption: Frederickson's Distributed BFS Algorithm reverse() function.
    
    For each process u, upon receipt of (reverse, b) from v:
    begin
        expectedreplies_u[v] set expectedreplies_u[v] - 1
        if b = true then
            Child_u set Child_u u {v}
            bvalue_u set true
        if forall n in Neigh_u: reply_u[n] = 0 then
            if parent_u != undef then
                send (reverse, bvalue_u) to parent_u
        else if bvalue_u = true then
            k set k + 1
            forall c in Child_u do
                send (explore, k) to c
                expectedreplies_i[n] set 1
        else
            terminate
    end

Correctness
~~~~~~~~~~~

The **correctness** of the BFS algorithm is established by ensuring the resulting tree accurately represents a BFS tree of the network graph upon the algorithm's termination.

- The algorithm builds the tree incrementally, starting from the root (initiator), ensuring each node is placed correctly according to BFS order.
- By induction, if nodes up to level `n` are correctly placed, a node at level `n+1` receives an "explore" message from level `n`, preserving the BFS order.
- Completeness is ensured as each node waits for replies from all neighbors before proceeding, thereby incorporating every reachable node in the network into the BFS tree.

**Safety** properties guarantee the algorithm's execution avoids incorrect states, such as cycles or nodes with multiple parents.

- Upon receiving its first "explore" message, a node sets its parent, preventing multiple parents or cycle creation.
- The propagation of forward and reverse messages through the tree structure prevents inconsistencies and ensures a cycle-free tree.


Complexity 
~~~~~~~~~~
The construction of the BFS tree uses at most |V | exploration rounds. In each round, an edge of the BFS tree carries at most one ⟨forward⟩ and one replying ⟨reverse⟩ message. In total, each edge carries at most one ⟨explore⟩ message and one replying ⟨reverse⟩ message. The worst-case message complexity is thus O(|V |2). As level f + 1 is computed in 2(f + 1) time units, the worst-case message and time complexity are the same:

    1. **Time Complexity**  Frederickson's Distributed BFS Algorithm :ref:`Algorithm <fredericksons_algo>` takes at most O(V^2) time units to complete where N is number of nodes in the given network.
    2. **Message Complexity:** Frederickson's Distributed BFS Algorithm :ref:`Algorithm <fredericksons_algo>` requires |V^2| control messages over the nodes.
