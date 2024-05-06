.. include:: substitutions.rst

Conclusion
==========

..
    In general a short summarizing paragraph will do, and under no circumstances should the paragraph simply repeat material from the Abstract or Introduction. In some cases it's possible to now make the original claims more concrete, e.g., by referring to quantitative performance results [Widom2006].

    The conclusion is where you build upon your discussion and try to refer your findings to other research and to the world at large. In a short research paper, it may be a paragraph or two, or practically non-existent. In a dissertation, it may well be the most important part of the entire paper - not only does it describe the results and discussion in detail, it emphasizes the importance of the results in the field, and ties it in with the previous research. Some research papers require a recommendations section, postulating that further directions of the research, as well as highlighting how any flaws affected the results. In this case, you should suggest any improvements that could be made to the research design [Shuttleworth2016].

Chandy-Misra is a very intuitive algorithm with minimal messages types to understand. It uses a modified version of Dijkstra-Schonten's diffusing computations for algorithm termination which is also very intuitive to understand. Its implementation on AHCv2 allowed us to implement the algorithm on top of the link layer.

It is easy to visualize and follow the execution steps of Chandy-Misra. It follows a greedy approach to choose the shortest path while cancelling previously accepted path. Since Chandy-Misra nodes can change paths without synchronization, it may result faster than Merlin-Segall which uses update rounds.

..
    TODO After implementation