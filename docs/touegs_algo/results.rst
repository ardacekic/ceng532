.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the algorithm section we have discussed the two varients of the Toueg's distributed shortest path algorithm. We have implemented the full variant one by using AHCv2 environemnt. In this section we will be focusing on how the implemented algorithm works and the messaging between the nodes when the shortest path forms.

There are three types of messages Toueg's full-variant algorithm:

1. Messages ("INFO", "Child") are sent from u to x at the beginning of w -pivot round, if x is the parent of u in the tree Tw .
2. Messages ("INFO", "NotChild") are sent from u to x the beginning of w -pivot round, if x is not the parent of u in thetree Tw .
3. Messages ("DISTANCE", (pivot, D_pivot)) are sent during w -pivot round via every channel in the tree Tw to deliver the table Dw to each node that must use this value.

Results
~~~~~~~~

TODO: Buraya ring ve random graph için resultları ve figure 


Discussion
~~~~~~~~~~

TODO:Present and discuss main learning points.




.. [Shuttleworth2016] M. Shuttleworth. (2016) Writing methodology. `Online <https://explorable.com/writing-methodology>`_.