.. include:: substitutions.rst

|fredericksons_algo|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In 1985, Greg N. Frederickson outlined a Breadth-First Search Tree Algorithm in his paper A Single Source Shortest Path Algorithm for a Planar Distributed Network.

Distributed Algorithm:  Frederickson's Algorithm 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Frederickson's Distributed BFS Algorithm :**
Frederickson's Distributed BFS Algorithm, also known as the Distributed Breadth-First Search Algorithm, is a parallel algorithm for traversing a graph. It was developed by Greg N. Frederickson in 1985.
The algorithm is designed to run on a distributed system, where each node in the graph is represented by a separate processor. The algorithm is based on the concept of breadth-first search, where the nodes are visited in a level-by-level manner.

1. **The algorithm works as follows:** 
Each processor is assigned a node in the graph.
Each processor maintains a queue of nodes to be visited.
Each processor starts by visiting its assigned node and adding its neighbors to its queue.
Each processor then visits the nodes in its queue in a round-robin fashion.
When a processor visits a node, it adds its neighbors to its queue and marks the node as visited.
The algorithm terminates when all nodes have been visited.

2. **The algorithm has the following properties:** 
It is a parallel algorithm, which means it can be run on multiple processors simultaneously.
It is a distributed algorithm, which means each processor is responsible for a portion of the graph.
It is a breadth-first search algorithm, which means it visits nodes in a level-by-level manner.
It is a synchronous algorithm, which means all processors must reach the same state at the same time.

3. **The algorithm has several advantages over traditional breadth-first search algorithms:** 
It is more efficient than traditional BFS algorithms, as it can be run in parallel on multiple processors.
It is more scalable, as it can be run on large graphs with a large number of processors.
It is more robust, as it can handle graphs with cycles and disconnected components.

4. **The algorithm has some limitations:** 
It requires a large amount of communication between processors, which can be a bottleneck in large graphs.
It requires a synchronous communication model, which can be challenging to implement in practice.
It may not be suitable for graphs with a high degree of connectivity, as the communication overhead can become too large.


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

Example
~~~~~~~~

Provide an example for the distributed algorithm.

Correctness
~~~~~~~~~~~

Present Correctness, safety, liveness and fairness proofs.


Complexity 
~~~~~~~~~~
The construction of the BFS tree uses at most |V | exploration rounds. In each round, an edge of the BFS tree carries at most one ⟨forward⟩ and one replying ⟨reverse⟩ message. In total, each edge carries at most one ⟨explore⟩ message
9
and one replying ⟨reverse⟩ message. The worst-case message complexity is thus O(|V |2). As level f + 1 is computed in 2(f + 1) time units, the worst-case message and time complexity are the same:

    1. **Time Complexity**  Frederickson's Distributed BFS Algorithm :ref:`Algorithm <fredericksons_algo>` takes at most O(V^2) time units to complete where N is number of nodes in the given network.
    2. **Message Complexity:** Frederickson's Distributed BFS Algorithm :ref:`Algorithm <fredericksons_algo>` requires |V^2| control messages over the nodes.
