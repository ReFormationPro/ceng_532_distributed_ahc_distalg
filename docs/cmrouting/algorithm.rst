.. include:: substitutions.rst

|CMRouting|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
..
    Present any background information survey the related work. Provide citations.

As previously stated, |CMRouting| is based on [Dijkstra1980]_'s diffusing computations which explore the detection of the termination of distributed algorithms.
Chandy-Misra's algorithm uses diffusing computations for termination of its first phase. 
However, due to the infinite vertices they had to modify the diffusing computations in order to terminate the first phase. 
In their modification, they allow vertices to change their predecessors even when all acknowledgments are not received.

[Lakshmanan1989]_ created a synchronous version of the algorithm and analyzed its message and complexities. 
They report the synchronous version has O(\|V\|\|E\|) message complexity and O(\|V\|) time complexity. 
Then, they combine the algorithm with a synchronizer to create an asynchronous protocol with the same complexities. 
The synchronizer has O(m) message complexity and O(1) time complexity overhead.

TODO Add new papers


Distributed Algorithm: |CMRouting| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Chandy-Misra algorithm is a distributed algorithm designed to compute the shortest paths from a single source vertex to all other vertices in a network represented as a directed graph. 
The algorithm operates in two phases and leverages message passing between processes (representing vertices) to propagate path information and update distance estimates.

In phase 1, the vertices send distance and acknowledgement messages to each other. 
Distance messages allow the vertices to select a predecessor that provides the shortest path to the source vertex. 
When a distance message is received, the sender of the distance message waits for an acknowledgement message from receiver. 
The receiver sends this acknowledgement when the processing of the distance message is finished. 
For example, if the receiver has a shorter path to the destination than the one message reports, it simply sends an acknowledgement message to the sender to indicate it is done with it. 
If the distance of the receiver to the destination is greater than the distance in message plus link weight between the sender and the receiver, then the receiver reports this path to its neighbors and waits for acknowledgement from them.
The receiver waits for all acknowledgement messages from its neighbors before sending an acknowledgement to the sender.
Note that if a node has no neighbors other than the sender, it sends an acknowledgement to the sender immediately. 

Phase 2 terminates the algorithm.
This phase is required to avoid infinite loops (negative cycles) and infinite waitings (shortest paths are calculated but nodes still wait for shorter paths).
There are two messages in phase 2: "over-" and "over?". 
When a negative cycle is detected by a vertex, it sends "over-" message to all its neighbors.
Neighbors that are seeing the "over-" for the first time forward this message to their own neighbors.
All neighbors who receive "over-" message terminate phase 1 and exit. 
"over?" message is similar, however it is sent when a vertex receives all of the acknowledgement messages it expects.
One differense is, the initial "over?" message is sent by the destination node and the rest are sent by the nodes that receive an "over?" message, whereas the initial "over-" messages can be sent by any node.
Thus, one way to view "over?" messages is it is sent upon the destination node asking if all nodes has finished successfulyy whereas "over-" messages are the result of nodes attempting to terminate a negative cycle.


Below you can find pseudo code for how |CMRouting| runs on the nodes.
:ref:`Algorithm <_CMRoutingAlgorithmDestNodeLabel>` shows how the destination node initiates the algorithm to start the calculations of a route to itself.
:ref:`Algorithm <CMRoutingAlgorithmNonDestNodeLabel>` shows how non destination nodes handle distance and acknowledgement messages.

.. _CMRoutingAlgorithmNonDestNodeLabel:
.. code-block:: RST
    :linenos:
    :caption: Chandy Misra Routing Algorithm for Non-Destination Nodes
    
    Implements: CMRoutingNode Instance: node
    Uses: 
        Current predecessor of this node: pred
        Distance received from the predecessor: distance
        Number of unacknowledged messages: num
        Id of this node: self_id

    Events: Init, LengthMessageReceived, Acknowledgement
    Needs:

    OnInit: () do
        # Initially there is no predecessor
        pred = NULL
        # Initially the distance is infinite so that any valid path (of finite distance)
        # is accepted
        distance = INF
        # Initially no acknowledgement messages is expected
        num = 0
    
    OnLengthMessageReceived: ( msg(distance, node ) ) do
        # If the sender of the message is closer to the destination,
        # change the predecessor
        if msg.distance < distance then
            # Send acknowledge to the previous predecessor if not already sent
            if num > 0 then Trigger SendAcknowledge( pred )
            # Update our current predecessor and distance
            pred = msg.node; distance = msg.distance;
            # Iterate neighbors and send distance messages
            for neighbor != msg.node do
                # Calculate neighbor's distance on the current path and notify neighbor
                Trigger SendDistanceMsg( distance + neighbor_link_distance( neighbor ), self_id )
            # Update number of expected acknowledge messages
            num += { number of neighbors except msg.node }
            # If this is a leaf node, we do not wait for successor acknowledgements
            # to acknowledge the predecessor
            if num == 0 then Trigger SendAcknowledge( pred )
        else then
            # The reported path is not shorter than current path
            # Discard the path and acknowledge the end processing for this path
            Trigger SendAcknowledge( msg.node )

    OnAcknowledgement: ( ack( node ) ) do
        # Decrement the number of expected acknowledgements
        num -= 1
        # If no acknowledgements are expected anymore, we are done processing
        # the current path reported by `pred`.
        # Thus, send an acknowledgement here
        if num == 0 then Trigger SendAcknowledge( pred )

.. _CMRoutingAlgorithmDestNodeLabel:
.. code-block:: RST
    :linenos:
    :caption: Chandy Misra Routing Algorithm for The Destination Node
    
    Implements: CMRoutingNode Instance: node
    Uses: 
        Current predecessor of this node: pred
        Distance received from the predecessor: distance
        Number of unacknowledged messages: num
        Id of this node: self_id

    Events: Init, LengthMessageReceived, Acknowledgement
    Needs:

    OnInit: () do
        # Its distance to itself is zero
        distance = 0
        # There is no predecessor
        pred = NULL
        # No acknowledgement messages are currently expected
        num = 0
        # Iterate all neighbors to start the algorithm
        for neighbor do
            # Algorithm starts with a distance message from the destination node
            Trigger SendDistanceMsg( neighbor_link_distance( neighbor ), self_id )
            # Increase the number of acknowledge packets expected
            num += 1
    
    OnLengthMessageReceived: ( msg(distance, node ) ) do
        # Distance less than 0 means there is a negative cycle
        if distance < 0 then
            # Terminate phase 1 to exit infinite loop
            TerminatePhaseI()
            # Phase 2 always follows phase 1
            StartPhaseII()
        else then
            # Acknowledge the message to indicate end of processing for this route
            Trigger SendAcknowledge( msg.node )

    OnAcknowledgement: ( ack( node ) ) do
        # Decrement the number of expected acknowledgement messages
        num -= 1
        # If no other acknowledgement message is expected, start phase 2
        if num == 0 then TerminatePhaseI(); StartPhaseII();

Example
~~~~~~~~~~~
Let there be four nodes called A, B, C, and D. Set the link weights: A-B is 3, A-C is 2, B-C is 1, and C-D is 4. We will illustrate how Chandy-Misra algorithm calculates the shortest paths to A.

#. Node A sets its own distance to 0 and sends its neighbors B and C distance messages MSG(0 + neighbor_link_distance( B ), A) and MSG(0 + neighbor_link_distance( C ), A), respectively. Furthermore, A sets the number of expected acknowledgements to 2.
#. Node B receives the distance message MSG(3, A) and changes its distance from infinity to 3. It sends MSG(4, B) to C. Then increases number of expected acknowledgement messages to 1. Furthermore, B sets its predecessor to A.
#. Node C receives the distance message MSG(2, A) and changes its distance from infinity to 2. It sends MSG(3, C) to B and MSG(6, C) to D. Then increases the number of expected acknowledgement messages to 2. Furthermore, C sets its predecessor to A.
#. Node C receives the distance message MSG(4, B). Since C currently has distance 2 to sink, it just sends an acknowledgement message to B.
#. Node B receives the distance message MSG(3, C). Since B currently has distance 3 to sink, it just sends an acknowledgement message to C.
#. Node B receives the acknowledgement message from C and decreases the number of expected acknowledgement messages. This value reaches 0 and hence B sends an acknowledgement message to A.
#. Node B receives the acknowledgement message from B and decreases the number of expected acknowledgement messages. This value reaches 1.
#. Node A receives the acknowledgement message from A and decreases the number of expected acknowledgement messages. This value reaches 1.
#. Node D receives the distance message MSG(6, C). Changes its distance from infinity to 6 and sets C as its predecessor. It has no neighbors it can send distance message to, hence sends acknowledgement to C.
#. Node C receives the acknowledgement message from D and decreases the number of expected acknowledgement messages. This value reaches 0. Hence, sends A an acknowledgement message.
#. Node A receives the acknowledgement message. Then A decreases the number of expected acknowledgement messages to 0. Thus, A terminates phase 1 and starts phase 2.
#. Node A sends "over?" message to B and C, C sends "over?" message to B and D, B sends "over?" message to C.
#. Algorithm finishes.  

Correctness
~~~~~~~~~~~
..
    Present Correctness, safety, liveness and fairness (not an issue as distributed and nothing blocks anything important) proofs.

*Termination*: 
The algorithm starts with the destination node sending distance messages to its neighbors and waiting for acknowledgement messages.
Receiving an acknowledgement message indicates that the processing of the corresponding distance message has ended.
The first phase ends for a node when the node detects a negative cycle or all expected acknowledgement messages are received.
Now, consider two cases:

Assume there is no negative cycles. All nodes will receive distance messages from their neighbors.
Consider a non-destination node.
If the received distance by this node is larger than or equal to the minimal distance observed by it so far, it will send an acknowledgement to the sender.
Thus, all distance message senders but one of them will receive an acknowledgement in this way.
The last acknowledgement will be sent when all acknowledgement messages expected by this node are retrieved.
Thus, assuming that all acknowledgement messages will be retrieved, this node will send acknowledgement messages to all distance message senders, multiple times if they sent multiple distance messages.

To prove this, remember that there is no negative cycle. 
The minimal distance observed so far is bounded from below, all nodes will eventually reach the minimal distance (proof omitted).
After this, they will no longer send distance messages as the distance cannot get shorter and no new distance messages will be sent by them.
Thus, the number of expected acknowledgements will not increase anymore and it will reach zero (proof omitted).
Hence, all non-destination nodes will send as many acknowledgement messages as the distance messages they received.
Finally, the destination node will receive all its acknowledgement messages and terminate.

Now assume that there is a negative cycle.
Then the nodes on the cycle are by definition connected and they will receive distance messages from their predecessor on the cycle.
Eventually the first node of the negative cycle (the node on the cycle that is first observed) will receive a distance from the node on the end of the cycle.
Since the cycle is negative, this distance will be less than the minimal distance observed by the first node of the cycle so far.
Hence, a new iteration of the cycle will initiate and this will also report a lesser distance to the first node, triggering another erroneous iteration.
Observe that since distances are finite, and the cycle can repeat forever, one of the nodes on the cycle will eventually receive a negative distance.
This node will trigger phase 2, and the phase 1 will end.

Hence, in either case phase 1 always terminates.

*Correctness*: By the proof of termination, if there is negative cycle then this cycle will cause one node of the cycle to receive a distance message of negative distance.
This will trigger phase 2, and phase 2 "over-" messages will be sent to every neighbor, ending phase 1 for everyone and reaching the conclusion of "negative cycle" on all of the network.
Hence, negative cycle will always be detected.

If there is no negative cycle, then a minimum distance route to the destination exists. Again, it follows from the termination proof that distance reports are bounded from below by the minimum distance and the algorithm will not terminate until this bound is reached. Hence, it calculates the shortest path.

*Safety*: If an acknowledgement package is lost, the algorithm may not ever terminate as it has no counter-measure built-in for such a case. Furthermore, as the edge count increases the number of messages sent will increase just as much and may hog the network and disrupt the algorithm or other services.

*Fairness*: The algorithm is largely fair; however, some nodes might utilize network more than others, such as those that have more edges and those that are far from the destination. 

Complexity 
~~~~~~~~~~
.. 
    The shortest path computations start from the destination node and first nodes to calculate their distance correctly are those that are closer. Thus, time complexity increases as the distance of the nodes increases. 

1. **Time Complexity:** In [Lakshmanan1989]_'s analysis of the synchronous version of the algorithm, they determined that the time complexity is O(\|V\|)
2. **Message Complexity:** In [Lakshmanan1989]_'s analysis of the synchronous version of the algorithm, they determined that the message complexity is O(\|EV\|). The authors of the algorithm also state that each node only needs to keep the last message of a neighbor in the memory, so asynchronous version also requires O(\|EV\|) memory.

.. [Chandy1982] K. Mani Chandy and Jayadev Misra. "Distributed computation on graphs: Shortest path algorithms." Communications of the ACM 25.11 (1982): 833-837.
.. [Dijkstra1980] Edsger W. Dijkstra and Carel S. Scholten. "Termination detection for diffusing computations." Information Processing Letters 11.1 (1980): 1-4.
.. [Lakshmanan1989] K. B. Lakshmanan, Krishnaiyan Thulasiraman, and M. A. Comeau. 
    "An efficient distributed protocol for finding shortest paths in networks with negative weights." 
    IEEE Transactions on Software engineering 15.5 (1989): 639-644.

..
    Present theoretic complexity results in terms of number of messages and computational complexity.




    .. admonition:: EXAMPLE 

        Snapshot algorithms are fundamental tools in distributed systems, enabling the capture of consistent global states during system execution. These snapshots provide insights into the system's behavior, facilitating various tasks such as debugging, recovery from failures, and monitoring for properties like deadlock or termination. In this section, we delve into snapshot algorithms, focusing on two prominent ones: the Chandy-Lamport algorithm and the Lai-Yang algorithm. We will present the principles behind these algorithms, their implementation details, and compare their strengths and weaknesses.

        **Chandy-Lamport Snapshot Algorithm:**

        The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` [Lamport1985]_ , proposed by Leslie Lamport and K. Mani Chandy, aims to capture a consistent global state of a distributed system without halting its execution. It operates by injecting markers into the communication channels between processes, which propagate throughout the system, collecting local states as they traverse. Upon reaching all processes, these markers signify the completion of a global snapshot. This algorithm requires FIFO channels. There are no failures and all messages arrive intact and only once. Any process may initiate the snapshot algorithm. The snapshot algorithm does not interfere with the normal execution of the processes. Each process in the system records its local state and the state of its incoming channels.

        1. **Marker Propagation:** When a process initiates a snapshot, it sends markers along its outgoing communication channels.
        2. **Recording Local States:** Each process records its local state upon receiving a marker and continues forwarding it.
        3. **Snapshot Construction:** When a process receives markers from all incoming channels, it captures its local state along with the incoming messages as a part of the global snapshot.
        4. **Termination Detection:** The algorithm ensures that all markers have traversed the system, indicating the completion of the snapshot.


        .. _ChandyLamportSnapshotAlgorithm:

        .. code-block:: RST
            :linenos:
            :caption: Chandy-Lamport Snapshot Algorithm [Fokking2013]_.
                    
            bool recordedp, markerp[c] for all incoming channels c of p; 
            mess-queue statep[c] for all incoming channels c of p;

            If p wants to initiate a snapshot 
                perform procedure TakeSnapshotp;

            If p receives a basic message m through an incoming channel c0
            if recordedp = true and markerp[c0] = false then 
                statep[c0] ← append(statep[c0],m);
            end if

            If p receives ⟨marker⟩ through an incoming channel c0
                perform procedure TakeSnapshotp;
                markerp[c0] ← true;
                if markerp[c] = true for all incoming channels c of p then
                    terminate; 
                end if

            Procedure TakeSnapshotp
            if recordedp = false then
                recordedp ← true;
                send ⟨marker⟩ into each outgoing channel of p; 
                take a local snapshot of the state of p;
            end if


        **Example**

        DRAW FIGURES REPRESENTING THE EXAMPLE AND EXPLAIN USING THE FIGURE. Imagine a distributed system with three processes, labeled Process A, Process B, and Process C, connected by communication channels. When Process A initiates a snapshot, it sends a marker along its outgoing channel. Upon receiving the marker, Process B marks its local state and forwards the marker to Process C. Similarly, Process C marks its state upon receiving the marker. As the marker propagates back through the channels, each process records the messages it sends or receives after marking its state. Finally, once the marker returns to Process A, it collects the markers and recorded states from all processes to construct a consistent global snapshot of the distributed system. This example demonstrates how the Chandy-Lamport algorithm captures a snapshot without halting the system's execution, facilitating analysis and debugging in distributed environments.


        **Correctness:**
        
        *Termination (liveness)*: As each process initiates a snapshot and sends at most one marker message, the snapshot algorithm activity terminates within a finite timeframe. If process p has taken a snapshot by this point, and q is a neighbor of p, then q has also taken a snapshot. This is because the marker message sent by p has been received by q, prompting q to take a snapshot if it hadn't already done so. Since at least one process initiated the algorithm, at least one process has taken a snapshot; moreover, the network's connectivity ensures that all processes have taken a snapshot [Tel2001]_.

        *Correctness*: We need to demonstrate that the resulting snapshot is feasible, meaning that each post-shot (basic) message is received during a post-shot event. Consider a post-shot message, denoted as m, sent from process p to process q. Before transmitting m, process p captured a local snapshot and dispatched a marker message to all its neighbors, including q. As the channels are FIFO (first-in-first-out), q received this marker message before receiving m. As per the algorithm's protocol, q took its snapshot upon receiving this marker message or earlier. Consequently, the receipt of m by q constitutes a post-shot event [Tel2001]_.

        **Complexity:**

        1. **Time Complexity**  The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` takes at most O(D) time units to complete where D is ...
        2. **Message Complexity:** The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` requires 2|E| control messages.


        **Lai-Yang Snapshot Algorithm:**

        The Lai-Yang algorithm also captures a consistent global snapshot of a distributed system. Lai and Yang proposed a modification of Chandy-Lamport's algorithm for distributed snapshot on a network of processes where the channels need not be FIFO. ALGORTHM, FURTHER DETAILS

    .. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
    .. [Tel2001] Gerard Tel, Introduction to Distributed Algorithms, CAMBRIDGE UNIVERSITY PRESS, 2001
    .. [Lamport1985] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.