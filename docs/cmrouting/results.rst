.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..
  TODO After implementation


The pseudocode and the explanations were quite easy to follow. Although we had a couple of uncertainties we needed to figure out ourselves. Here is a list of them:

- The paper says "over?" messages should be sent to those who have not received such a message. This cannot be known by the nodes themselves and attempting to learn this by asking is inefficient. Instead, in our implementation a "overqm_msgs_sent" flag is used to indicate whether this "over?" message is sent to all of the neighbors or not is stored. This flag is initially false and when the node sends "over?" messages to all its neighbors, it is set to true. Thus, "over?" messages are only sent once. Since if a node receives "over?" message twice, the second one just gets ignored, this solves the issue quite nicely.
- Similarly, the paper does not mention how to handle "over?" and "over-" messages by the destination node. "over?" message is initially sent by the destination node so it does not make sense to handle such messages, thus we left its handler empty. Similarly, the behaviour of "over-" message handler was not mentioned. Two meaningful solutions exist: Leaving it empty or forwarding it to neighbors once. After a careful examination of both ways, we noticed that the algorithm terminates the either way. So we went with the simpler one, ignoring it.


..
  Writing the methodology lies at the core of the paper, and fulfills one of the basic principles underlying the scientific method. Any scientific paper needs to be verifiable by other researchers, so that they can review the results by replicating the experiment and guaranteeing the validity. To assist this, you need to give a completely accurate description of the equipment and the techniques used for gathering the data [Shuttleworth2016]_.

  Other scientists are not going to take your word for it, and they want to be able to evaluate whether your methodology is sound. In addition, it is useful for the reader to understand how you obtained your data, because it allows them to evaluate the quality of the results. For example, if you were trying to obtain data about shopping preferences, you will obtain different results from a multiple-choice questionnaire than from a series of open interviews. Writing methodology allows the reader to make their own decision about the validity of the data. If the research about shopping preferences were built upon a single case study, it would have little external validity, and the reader would treat the results with the contempt that they deserve [Shuttleworth2016]_.

  Describe the materials and equipment used in the research. Explain how the samples were gathered, any randomization techniques and how the samples were prepared. Explain how the measurements were made and what calculations were performed upon the raw data. Describe the statistical techniques used upon the data [Shuttleworth2016]_.

  Present any important details of your implementation here.

Results
~~~~~~~~


We tested the implementation on the following graphs:

+-----------------------------------------+
| .. figure:: ./figures/karate-club.jpg   |
|   :alt: Karate club graph visualized    |
|   :width: 500                           |
|                                         |
|   Karate club graph visualized          |
|                                         |
+-----------------------------------------+
In karate club graph, it gave the following predecessors for nodes when the destination node number is 7:

0: 7, 1: 7, 2: 7, 3: 7, 4: 0, 5: 0, 6: 0, 7: -1, 8: 0, 9: 2, 10: 0, 11: 0, 12: 0, 13: 0, 14: 33, 15: 32, 16: 5, 17: 0, 18: 32, 19: 0, 20: 33, 21: 0, 22: 32, 23: 33, 24: 31, 25: 24, 26: 33, 27: 2, 28: 2, 29: 33, 30: 1, 31: 0, 32: 2, 33: 19


+-----------------------------------------+
| .. figure:: ./figures/simple-graph.png  |
|   :alt: Simple graph visualized         |
|   :width: 500                           |
|                                         |
|   Simple graph visualized               |
|                                         |
+-----------------------------------------+
In order to verify the correctness of the implementation with manual calculations, we tried with a simple graph. The implementation gave the following predecessors for nodes when the destination node number is 'a':

'a': -1, 'b': 'a', 'c': 'a', 'd': 'a', 'e': 'c', 'f': 'c'

Next, we plotted execution times against node counts and edge counts.

+----------------------------------------------------------------------------------+
| .. figure:: ./figures/execution-time-vs-node-count.jpg                           |
|   :alt: Simple graph visualized                                                  |
|   :width: 500                                                                    |
|                                                                                  |
|   Execution time vs Node Counts, where edge count is fixed to 2525               |
|                                                                                  |
+----------------------------------------------------------------------------------+

..
  In the experimental results we see above, the execution times linearly increase as the node count increases. This is expected as we noted in the algorithm section, time complexity is shown to be O(\|V\|) by [Lakshmanan1989]_.

In the experimental results we see above, the execution times get lower at a decelerating rate. As mentioned in the algorithm section, [Lakshmanan1989]_ has shown time complexity of Chandy-Misra is O(\|V\|). We cannot see this result from these results.

+-------------------------------------------------------------------+
| .. figure:: ./figures/execution-time-vs-edge-count.jpg            |
|   :alt: Simple graph visualized                                   |
|   :width: 500                                                     |
|                                                                   |
|   Execution time vs Edge Counts, where node count is fixed to 100 |
|                                                                   |
+-------------------------------------------------------------------+

In the result shown above, execution times seem to increase linearly as the edge counts increase. Comparing the two charts above, the execution times correlate with edge count but negatively correlate with node counts. Hence, it is likely that the execution times correlate with edges per node.

..
  Present your AHCv2 run results, plot figures.


  This is probably the most variable part of any research paper, and depends upon the results and aims of the experiment. For quantitative research, it is a presentation of the numerical results and data, whereas for qualitative research it should be a broader discussion of trends, without going into too much detail. For research generating a lot of results, then it is better to include tables or graphs of the analyzed data and leave the raw data in the appendix, so that a researcher can follow up and check your calculations. A commentary is essential to linking the results together, rather than displaying isolated and unconnected charts, figures and findings. It can be quite difficulty to find a good balance between the results and the discussion section, because some findings, especially in a quantitative or descriptive experiment, will fall into a grey area. As long as you not repeat yourself to often, then there should be no major problem. It is best to try to find a middle course, where you give a general overview of the data and then expand upon it in the discussion - you should try to keep your own opinions and interpretations out of the results section, saving that for the discussion [Shuttleworth2016]_.


  .. image:: figures/CDFInterferecePowerFromKthNode2.png
    :width: 400
    :alt: Impact of interference power


  .. list-table:: Title
    :widths: 25 25 50
    :header-rows: 1

    * - Heading row 1, column 1
      - Heading row 1, column 2
      - Heading row 1, column 3
    * - Row 1, column 1
      -
      - Row 1, column 3
    * - Row 2, column 1
      - Row 2, column 2
      - Row 2, column 3

Discussion
~~~~~~~~~~
..
  TODO After implementation

Unlike Merlin-Segall, it does not handle topological changes. However, due to less number of functionalities it uses less many messages. The algorithm was very intuitive and simple to implement.


.. [Lakshmanan1989] K. B. Lakshmanan, Krishnaiyan Thulasiraman, and M. A. Comeau. 
    "An efficient distributed protocol for finding shortest paths in networks with negative weights." 
    IEEE Transactions on Software engineering 15.5 (1989): 639-644.
..
  Present and discuss main learning points.




.. 
  [Shuttleworth2016] M. Shuttleworth. (2016) Writing methodology. `Online <https://explorable.com/writing-methodology>`_.