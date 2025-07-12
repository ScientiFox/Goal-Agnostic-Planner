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

 - _Lack of Reward Function_: Because the SAS model collects observed and prompted information- actions taken by the agent, and operates entirely on probabilities derived from these instance counts, no reward function is required to train GAP agents when maximizing probability or minimizing steps-to-goal. This makes the agent free of the bias and risk of poor design of an objective function. However, the algorithm can be used with costs, such as minimum expectation of cose (probability and cost in tandem), energy, time, or similar.

 - _Goal Agnosticism_: Because the algorithm's model counts SAS transitions, all such can be used to determine paths between any observed, non-disjoint states. As such, while we often specify a goal for termination of epochs, any reachable state can be sought using the same training data. Notably, this information (states and actions) requires no further input than standard SA model learners
 
 - _Optimality_: Addressed in detail in section **4.1 Optimality of GAP plans** in the attached paper, the combination of embedding optimality of the Array/Linked-lists and Dijkstra's algorithm ensures that plans produced by the GAP algorithm are stochastically optimal.

 - _Bounded Time Performance_: Addressed in detail in section _4.2.3 Derivation of Bounded Time Performance_
 in the attached paper, the Sequence Inference algorithm remits to analysis of the choice sequences of the agent as a MDP, from which demonstrates the probability of the system reaching the goal state increasing exponentially.

 - _Computational Efficiency_: Addressed in sections **3.3 Subgraph Maintenence Algorithm** and **3.4 Sequence Inference Algorithm**, the maintenance of the SAS hypergraph and maximal likelihood slide are constant bounded, and the inference algorithm is bounded in quadratic time, ensuring low-order polynomial computation time.

 - _Robustness to Error_: Addressed in detail in section **4.3 Analysis of Robustness under perturbation** the agent's dynamics under the MDP model can be used to hypothesize a further transfer function representing perturbations of the system, and goal convergance can be shown to hold under broad conditions.

 - _Abstraction Tolerance_: Addressed in section **4.4 Impact of Perturbed State on Performance**, the transfer functions previously mentioned can also be used examine state abstraction models on performance, and an exponential bounding measure for such derived, indicating tolerance of relatively aggressive abstractions.

 - _Reciprocal Convergence_: Addressed in section **4.5 Learning Convergence**, using the same mechanism used for error and abstraction analysis, the agent's learning is modeled as a progressively improving error mask, and goal convergence rates are shown to be statistically reciprocal as learning progresses.

   
<h3>Examples</h3>

- _Strips-type Problems_: Learning a problem form typical of traditional hierarchical AI planners, to demonstrate essential functionality of the algorithm. Additionally includes the injection of random error to illustrate robustness to these deviations.

- _TAXI and MAZE Problems_:

- _Tower of Hanoi Puzzle_:

- _Blocksworld Problem_:

- _Binary Addition Problem_:







