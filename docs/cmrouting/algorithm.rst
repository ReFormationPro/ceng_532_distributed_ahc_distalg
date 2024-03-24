.. include:: substitutions.rst

|CMRouting|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
..
    Present any background information survey the related work. Provide citations.

Distributed Algorithm: |CMRouting| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below you can find pseudo code for how |CMRouting| algorithm runs on the nodes.
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

    Events: Init, LengthMessageReceived
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

    Events: Init, LengthMessageReceived
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

Correctness
~~~~~~~~~~~
..
    Present Correctness, safety, liveness and fairness (not an issue as distributed and nothing blocks anything important) proofs.

*Termination (liveness)*: 
The algorithm starts with the destination node sending distance messages to its neighbors and waiting for acknowledgement messages.
Receiving an acknowledgement message indicates that the processing of the corresponding distance message has ended.
The first phase ends for a node when the node detects a negative cycle or all expected acknowledgement messages are received.
Now, consider two cases:

1- Assume there is no negative cycles. All nodes will receive distance messages from their neighbors.
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

2- Now assume that there is a negative cycle.
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

If there is no negative cycle, then a minimum distance route to the destination exists.
We want to show the algorithm will calculate a minimum distance route to the destination node for all its non-destination nodes.
TODO

Complexity 
~~~~~~~~~~

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