.. include:: substitutions.rst

|touegs_algo|
=========================================

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The concept of distributed computing and the challenges associated with it, especially in terms of reliability and coordination of distributed systems, are critical in understanding Toueg's algorithm. The background of this algorithm is deeply rooted in solving the all-pairs shortest paths problem in a distributed manner, akin to the centralized Floyd-Warshall algorithm which is fundamental in graph theory for computing shortest paths between all pairs of nodes in a weighted graph.

Toueg's algorithm modifies the Floyd-Warshall approach to suit distributed systems by enabling each node to compute shortest paths independently using localized information and communication with other nodes. This adaptation is essential for applications where data is too large to be processed centrally or where the system is geographically dispersed.

The related work primarily involves the exploration of various shortest path algorithms like Dijkstra’s and Bellman-Ford, which are traditionally designed for single-source shortest path problems. However, unlike these, Floyd-Warshall and by extension Toueg’s algorithm, focus on all-pairs shortest paths, which is more comprehensive for network analysis.

Researchers have further explored these concepts by integrating theories of fault tolerance and algorithms designed to enhance the reliability of distributed operations. The advancements in multi-core and multi-threaded computing have also influenced the development of more efficient distributed algorithms by allowing parallel processing and reducing computation time significantly.

In summary, the background and related work surrounding Toueg's algorithm highlight the evolution of network analysis algorithms from centralized to distributed frameworks, addressing both the computational and reliability challenges posed by modern distributed systems. This research is crucial for the ongoing development of more robust and efficient distributed computing environments.

Distributed Algorithm: |touegs_algo| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The pseudo code of the Toueg's simple variant and full variant will be on this section. 

Toueg's algorithm is ::

1. An distributed algorithm
2. Based on Floyd-Warshall
3. Each node knows it's neighbours and the weight of their connection
4. N messages are being passed through each channel/connection and N*E in total (with E being the number of Edges)


.. _TouegsSimpleAlgorithmLabel:
.. code-block:: RST
    :caption: Toueg's algorithm (simple variant)

    var S_u : set of nodes;
    D_u : array of weights; Nb_u : array of nodes;

    begin S_u := null;
    for all v in V do
       if v = u then begin D_u[v] := 0; Nb_u[v] := undef end
       else if v in Neigh_u
          then begin D_u[v] := w_uv; Nb_u[v] := v end
          else begin D_u[v] := inf; Nb_u[v] := undef end;

    while S_u != V do
       begin pick w from V \ S_u ;
       (* All processes choose the same pivot node w *)
       if u = w then “broadcast D_w” else “receive D_w”;
       for all v in V do
          if D_u[w] + D_w[v] < D_u[v] then
             begin D_u[v] := D_u[w] + D_w[v]; Nb_u[v] := Nb_u[w] end;
             S_u := S_u u {w}
       end
    end

About simple algorithm ::
   
• Floyd-Warshall algorithm with variables split over nodes of the network.
• Every node has information on the shortest route (found so far) to every other node.
• In every step every node requires distance information from the pivot node, so the pivot node broadcasts the information over the entire net.
• The simple algorithm’s major problem is that it requires a broadcast to all nodes in the network before routing tables have been calculated! It also transmits data unnecessarily.

.. code-block:: RST
    :caption: Toueg's algorithm (full variant)

    var S_u : set of nodes;
    D_u : array of weights;
    Nb_u : array of nodes;

    begin S_u := null;
    forall v in V do
       if v = u
          then begin D_u[v] := 0; Nb_u[v] := undef end
       else if v in Neigh_u
          then begin D_u[v] := w_uv; Nb_u[v] := v end
       else begin D_u[v] := inf; Nb_u[v] := undef end;
   
    //Detecting son nodes
    while S_u != V do
       begin pick w from V \ S_u;
       forall x in Neigh_u do
          if Nb_u[w] = x then send ⟨ys, w⟩ to x
          else send ⟨nys, w⟩ to x;

       rec_u := 0; (* u must receive |Neigh_u| messages *)
       while rec_u < |Neigh_u| do
          begin receive ⟨ys, w⟩ or ⟨nys, w⟩; rec_u := rec_u + 1 end;

     //updating tables
    if D_u[w] < inf then (* participate in w-pivot round *)
       begin if u != w then receive ⟨dtab, w, D⟩ from Nb_u[w];
       forall x in Neigh_u do
          if ⟨ys, w⟩ was received from x
             then send ⟨dtab, w, D⟩ to x;

       forall v in V do (* local processing of a pivot node w *)
          if D_u[w] + D[v] < D_u[v] then
             begin D_u[v] := D_u[w] + D[v]; Nb_u[v] := Nb_u[w] end;

       S_u := S_u u {w}
    end
    end    

About updated variant ::

• If Du[w] = inf in the main loop, the test is always false. Thus, a node u for which Du[w] = inf need not receive data from pivot w.
• In other words, w only needs to send routing data to nodes that have a next hop node and are therefore part of its sink tree Tw.
• However, although each node knows its parent in Tw, the parent does not know its children.
• Each node tells it neighbour every iteration whether it is a neighbour or not.

**How improved algorithm works:**

1. The main loop is executed (|V |) times. It contains a loop with (|V |) iterations (and a few with O(|V |) iterations) and loop contents that take O(1) time. The total running time is O(|V |^2).
2. The improved algorithm removes the need for broadcasting.
3. Assume that a pair consisting of an edge/path weight and a node name can be sent in W bits.
4. Then, the child and nochild messages are W bits.
5. The Dw messages are |V |W bits.
6. 2 child/nochild messages per edge and iteration and one table transfer per vertex at the most per iteration.
7. O(|V|^3W)bitstotal.

We will implement and collect results form full-variant algorithm in this document. First one easy to implement. Every node must collect the distance from every node pair O(N^3) messages and select the miniumum path if exists.

Complexity 
~~~~~~~~~~

Time complexity of the Toueg's algortihm is : O(N^3)

The message complexity of the Toueg's algorithm is: O(|V|^3W) bits in total.
