<img width="2776" height="1856" alt="GAP digest" src="https://github.com/user-attachments/assets/70d17bf5-a66d-4c5f-bc38-d010ff007cd6" />

<h2>Goal Agnostic Planning Algorithm</h2>

The Goal Agnostic Planner, or GAP, algorithm is a hybrid fusion of classical AI techniques for problem solving and machine learning concepts derived from reinforcement learning and probabilistic inference. It implements a State/Action/State model for learning, with a likelihood-maximization implementation of Dijkstra's algorithm on a hypergraph structure to represent this SAS space. For efficiency, it implements a dynamic Array/Sorted linked-list to guarantee the existance of a maximal probability projection of the hypergraph is always available. This combination of techniques results in several favorable planning and problem-solvign features, including stochastic error tolerance, the absence of need for a reward function, rapid learning rates, computational efficiency, input abstraction compatibility, and, naturally, agnosticism of training to the selected goal state. Further, its structure allows direct mathematical modeling which allows all these properties to be proved from theoretical analysis.

This repository contains a library implementing the GAP algorithm, pDij_type2.py, as well as several different test suites. These tests implement GAP learning on several problems of varying and adjustable levels of complexity, and are the tests which underwrite the data and analysis within the, also attached, paper "Goal Agnostic Learning and Planning without Reward Functions". This paper describes the algorithm mathematical analysis thereof, experimental validation, and additional modifications for training and implementation in exacting detail, and is the primary reference for the algorithm.

The descriptions below are, therefor, high-level overviews.

<h3>Mechanisms</h3>
There are three primary components which comprise the GAP algorithm, and underwrite its efficacy, Dijkstra's algorithm for maximum-likelihood path planning, the State/Action/State hypergraph, and Sorted Array/Linked-lists.

- _State/Action/State Hybergraph_: This learning model records instances of actions causing transitions between states. Because it is presumed that many actions can be taken from a given state, and each action may have more than onr result, depending on conditions, this structure represents a hypergraph instead of a standard graph.

- _Dijkstra's Algorithm for Maximum-likelihood path planning_: This application treats the action mediated transitions between actions as probabilistic, and uses joint probability maximization as the measure for identification of an optimal path, defined by the actions most likely to effect any given state transition.

- _Array/Sorted Linked Lists_: This data structure represents the SAS hypergraph as a collection of array-indexed sorted linked lists, allowing reflexive referencing between SAS triplets and making a maximum-probability graph slice of the hypergraph always available.

<h3>Features</h3>

<h3>Examples</h3>

- _Strips-type Problems_:

- _TAXI and MAZE Problems_:

- _Tower of Hanoi Puzzle_:

- _Blocksworld Problem_:

- _Binary Addition Problem_:







