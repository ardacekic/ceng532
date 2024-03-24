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

Toueg's algorithm (simple variant)
==================================

.. code-block:: none

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

Toueg's algorithm (full variant)
==================================

.. code-block:: none

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
Complexity 
~~~~~~~~~~

Message and time complexity of the Toueg's algortihm is : O(N²)