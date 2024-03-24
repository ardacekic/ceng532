.. include:: substitutions.rst

|touegs_algo|
=========================================

Distributed Algorithm: |touegs_algo| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The peseudo code of the Toueg's simple variant and full variant will be on this section. 

Toueg's algorithm is:

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

• About simple algorithm:
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

• About updated variant:
• If Du[w] = inf in the main loop, the test is always false. Thus, a node u for which Du[w] = inf need not receive data from pivot w.
• In other words, w only needs to send routing data to nodes that have a next hop node and are therefore part of its sink tree Tw.
• However, although each node knows its parent in Tw, the parent does not know its children.
• Each node tells it neighbour every iteration whether it is a neighbour or not.

Complexity 
~~~~~~~~~~

Message and time complexity of the Toueg's algortihm is : O(N²)