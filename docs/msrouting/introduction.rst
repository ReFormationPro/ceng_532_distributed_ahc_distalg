.. include:: substitutions.rst

Introduction
============

**Introduction to Merlin-Segall Routing Algorithm**

In the realm of communication networks, efficient routing protocols play a pivotal role in ensuring seamless data transmission between nodes. One such algorithm that has garnered attention for its failsafe distributed routing capabilities is the Merlin-Segall algorithm. This algorithm, developed by P. M. Merlin and A. Segall, addresses the challenge of constructing and maintaining routing tables in dynamic network environments.

The problem at hand revolves around the need for a routing protocol that can adapt to network changes, recover from failures, and provide loop-free routes to each destination at all times. In today's interconnected world, where data transfer is the lifeblood of various applications and services, the ability to establish reliable communication paths is crucial. Without a robust routing protocol in place, network disruptions, bottlenecks, and data loss can impede the flow of information, leading to inefficiencies and potential service disruptions.

The significance of solving this problem lies in the ability to maintain optimal communication paths in the face of network disruptions, thereby minimizing delays and ensuring data integrity. Failure to address this challenge can result in network congestion, packet loss, and inefficient data routing, ultimately impacting the overall performance of the network.

The complexity of this problem stems from the dynamic nature of communication networks, where traditional routing approaches may fall short in handling rapid changes in network topology and link failures. Naive approaches often struggle to provide failsafe routing solutions that can adapt to evolving network conditions.

Previous solutions in the realm of distributed routing algorithms have faced limitations in terms of recovery from arbitrary topological changes and ensuring loop-free routes at all times. The Merlin-Segall algorithm sets itself apart by introducing features that guarantee recovery from network disruptions and maintain loop-free routes to each destination, even in the face of dynamic changes.

Key components of the Merlin-Segall algorithm include adaptive routing mechanisms, failsafe distributed routing protocols, and efficient recovery strategies. By leveraging these components, the algorithm aims to provide robust and efficient routing solutions in dynamic communication networks.


TODO Fix the following:

Contributions:

- Introduction of a failsafe distributed routing protocol for dynamic network environments (Section 2)
- Analysis of the key features and challenges of the Merlin-Segall algorithm (Section 3)
- Comparison with previous routing solutions and highlighting the unique aspects of the proposed algorithm (Section 4)
- Implementation of the algorithm in the AHCv2 platform and benchmarking results (Section 5)
- Discussion on the limitations and future research directions of the Merlin-Segall algorithm (Section 6)

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