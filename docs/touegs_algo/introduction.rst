.. include:: substitutions.rst

Introduction
============

Running code on a single computing unit, typically a thread or core, often falls short in efficiency and speed for demanding computational tasks. This limitation has driven the evolution of multi-core and multi-threaded CPUs, enabling simultaneous execution of multiple tasks or processes. This advancement underpins parallel computing, a methodology designed to amplify computing power and speed.

Yet, an even more ambitious approach involves dividing a program into components executable by entirely separate machines. This model gives rise to distributed systems, in which distinct computers communicate over a network. Such systems can be architected in various configurations, including client-server, peer-to-peer, and n-tier models.

The essence of the distinction between parallel and distributed computing lies in their communication mechanisms. Parallel computing, particularly within multi-core systems, benefits from shared memory access, allowing compute units (CPU cores) to communicate swiftly via the bus. Conversely, distributed systems operate on a model of distributed memory, where each computer possesses its own memory, necessitating message passing over a network for inter-computer communication.

Routing algorithms are those that give us the shortest path to an specific destination. This means that we calculate the shortest paths from one or more vertices to the others and can then use this routing matrix to see which node is the best to send a package to, if we want it to end up on another node in the best and most efficient way.

Toueg's distributed algorithm for this problem is based on the centralized Floyd-Warshall algorithm for computing shortest paths between all pairs of nodes.

• Floyd-Warshall algorithm with variables split over nodes of the network.
• Every node has information on the shortest route (found so far) to every other node.
• In every step every node requires distance information from the pivot node, so the pivot node broadcasts the information over the entire net.
• The simple algorithm’s major problem is that it requires a broadcast to all nodes in the network before routing tables have been calculated! It also transmits data unnecessarily.

There are two types of toueg's algorithm implementations. We will be focusing on them in algorithm section.