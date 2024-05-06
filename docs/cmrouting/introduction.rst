.. include:: substitutions.rst

Introduction
============

In the field of distributed shortest path algorithms, the main difficulty lies in effectively calculating the shortest routes from a specific starting point to all other points in a graph that is both weighted and directed, even when there are negative cycles present. The complexity of this problem stems from the need to navigate through the graph while considering negative cycle scenarios, optimizing path lengths, and ensuring accurate computations in a distributed computing environment.

Distributed shortest path algorithms are both intriguing and critical due to their pivotal role in network optimization, routing efficiency, and resource allocation. Successfully solving the shortest path problem offers numerous advantages. It enhances decision-making processes, improves network performance, and reduces operational costs by identifying optimal routes and minimizing traversal distances. Failing to address this problem may lead to suboptimal routing decisions, increased resource consumption, and inefficiencies in network operations, impacting overall system performance and scalability.

The inherent difficulty in computing shortest paths in distributed systems arises from the decentralized and asynchronous nature of network communication. Naive approaches often falter in handling the complexities of negative cycles, message ordering, fault tolerance, and scalability. Concurrency issues, inaccurate message sequencing, and synchronization challenges can hinder the accuracy of path computations, while insufficient fault tolerance mechanisms may compromise the reliability of the algorithm. Overcoming these obstacles necessitates sophisticated algorithms that strike a balance between correctness, efficiency, fault tolerance, and scalability in distributed environments.

The persistent challenge of computing shortest paths in distributed systems, particularly within the context of the proposed algorithm, lies in addressing the complexities of negative cycles, optimizing message passing protocols, ensuring fault tolerance mechanisms, and maintaining scalability. Though the authors have not made a comparison of their algorithm to previous existing algorithms, they stated that they used Dijkstra and Scholten's diffusing computation for their message communication protocol [Chandy1982]_. Therefore, the solution can be thought of as an extension of the diffusing computation.

..
    Previous solutions may have encountered limitations in scalability, fault tolerance, or computational efficiency, necessitating innovative approaches to enhance the algorithm's performance and applicability in real-world scenarios.

Chandy-Misra distributed algorithm for computing shortest paths encompasses novel message-passing protocols, diffusing computation principles, and fault tolerance mechanisms tailored for accurate path computations in the presence of negative cycles. 
By leveraging innovative techniques and addressing the limitations of existing solutions, the algorithm aims to provide efficient and reliable shortest path computations in distributed graph networks, offering insights into network optimization and routing efficiency while ensuring scalability and fault tolerance in dynamic computing environments.
In this project, we provide an implementation for the algorithm on the AHCv2 platform.
AHCv2 allows us to simulate multiple layers, most notably application, overlay network, and link layer.
It allows us to implement the algorithm in a modular way with high customization options on each layer.

Our primary contributions consist of the following:

- Providing an implementation of Chandy-Misra algorithm on AHCv2
- Demonstrating the algorithm on application, Chandy-Misra overlay, and link layers
- By discussing implementation issues, we are helping others to understand the paper and the algorithm and with creating new implementations.


..
    TODO Add section descriptions here.

.. [Chandy1982]  K. Mani Chandy, and Jayadev Misra. "Distributed computation on graphs: Shortest path algorithms." Communications of the ACM 25.11 (1982): 833-837.

..
    If you would like to get a good grade for your project, you have to write a good report.  Your project will be assessed mostly based on the report. Examiners are not mind-readers, and cannot give credit for work which you have done but not included in the report [York2017]_.

    Here is the Stanford InfoLab's patented five-point structure for Introductions. Unless there's a good argument against it, the Introduction should consist of five paragraphs answering the following five questions:

    - What is the problem?
    - Why is it interesting and important? What do you gain when you solve the problem, and what do you miss if you do not solve it?
    - Why is it hard? (e.g., why do naive approaches fail?)
    - Why hasn't it been solved before? What's wrong with previous proposed solutions? How does yours differ?
    - What are the key components of your approach and results including any specific limitations.

    Then have a penultimate paragraph or subsection: "Contributions". It should list the major contributions in bullet form, mentioning in which sections they can be found. This material doubles as an outline of the rest of the paper, saving space and eliminating redundancy.

    .. [York2017]  York University. (2017) How to write a project report.



    .. admonition:: EXAMPLE 

        In the realm of snapshot algorithms for distributed systems, the fundamental problem lies in capturing a consistent global state without interrupting the ongoing execution of processes and avoiding excessive overhead. The challenges involve managing concurrency, ensuring accurate message ordering, providing fault tolerance to handle process failures, optimizing efficiency to minimize computational and communication overhead, and maintaining scalability as the system expands. Successfully addressing these challenges is crucial for designing snapshot algorithms that accurately reflect the distributed system's dynamic state while preserving efficiency and resilience.,
        
        Snapshot algorithms are both interesting and important due to their pivotal role in understanding, managing, and troubleshooting distributed systems. Solving the problem of capturing consistent global states in a distributed environment offers several significant benefits. Firstly, it provides invaluable insights into the system's behavior, facilitating tasks such as debugging, performance analysis, and identifying issues like deadlocks or message race conditions. Moreover, snapshot algorithms enable efficient recovery from failures by providing checkpoints that allow systems to resume operation from a known, consistent state. Additionally, they aid in ensuring system correctness by verifying properties like termination or the absence of deadlock. Without solving this problem, distributed systems would lack the capability to effectively diagnose and resolve issues, leading to increased downtime, inefficiencies, and potentially catastrophic failures. The absence of snapshot algorithms would hinder the development, deployment, and management of robust and reliable distributed systems, limiting their usability and scalability in modern computing environments. Thus, addressing this problem is critical for advancing the field of distributed systems and maximizing the reliability and efficiency of distributed computing infrastructures.

        Capturing consistent global states in distributed systems poses significant challenges due to their decentralized, asynchronous nature. Naive approaches often fail due to complexities such as concurrency, message ordering, synchronization, fault tolerance, and scalability. Concurrency and ordering issues may lead to inconsistent snapshots, while synchronization difficulties hinder performance. Inadequate fault tolerance can result in incomplete or incorrect snapshots, jeopardizing system recovery and fault diagnosis. Additionally, inefficient approaches may impose excessive overhead, impacting system performance. Overcoming these challenges requires sophisticated algorithms that balance correctness, efficiency, fault tolerance, and scalability, navigating the inherent trade-offs of distributed systems to capture accurate global states without disrupting system operation.

        The persistent challenge of capturing consistent global states in distributed systems, particularly within the context of the Chandy-Lamport Algorithm, arises from the algorithm's inherent complexities and the dynamic nature of distributed environments. While the Chandy-Lamport Algorithm offers a promising approach by utilizing marker propagation to capture snapshots without halting the system's execution, its implementation faces obstacles such as concurrency management, ensuring accurate message ordering, and handling fault tolerance. Previous attempts at solving these challenges with the Chandy-Lamport Algorithm may have been hindered by their complexity, limited scalability, or inability to adapt to changing system conditions. Thus, achieving a comprehensive resolution within the Chandy-Lamport framework requires addressing these concerns through innovative approaches that optimize for correctness, efficiency, fault tolerance, and scalability while considering the evolving requirements of distributed systems.

        The Chandy-Lamport Algorithm is a key method for capturing consistent global snapshots in distributed systems, comprising the initiation of marker propagation, recording of local states by processes upon marker reception, and subsequent snapshot reconstruction. It allows for the capture of snapshots without halting system execution, facilitating concurrent operations and serving various purposes like debugging and failure recovery. However, the algorithm exhibits limitations including increased message overhead due to marker propagation, challenges in managing concurrency which may affect snapshot accuracy, potential difficulties in handling faults during snapshot collection, and scalability concerns as system size grows. Despite these limitations, the Chandy-Lamport Algorithm remains foundational in distributed systems, driving further research in snapshot capture techniques. DETAILS OF Lai-Yang Algorithm.

        Our primary contributions consist of the following:
        
        - Implementation of both the Chandy-Lamport Algorithm and the Lai-Yang Algorithm on the AHCv2 platform. The implementation specifics are detailed in Section XX.
        - Examination of the performance of these algorithms across diverse topologies and usage scenarios. Results from these investigations are outlined in Section XXX.
        - Comprehensive comparison and contrast of the algorithms based on criteria such as accuracy, overhead, complexity, and fault tolerance. Key insights derived from these comparisons are elaborated upon in Section XXXX.