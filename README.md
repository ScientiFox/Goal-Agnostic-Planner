<img width="2776" height="1856" alt="GAP digest" src="https://github.com/user-attachments/assets/70d17bf5-a66d-4c5f-bc38-d010ff007cd6" />

<h2>Goal Agnostic Planning Algorithm</h2>

The Goal Agnostic Planner, or GAP, algorithm is a hybrid fusion of classical AI techniques for problem solving and machine learning concepts derived from reinforcement learning and probabilistic inference. It implements a State/Action/State model for learning, with a likelihood-maximization implementation of Dijkstra's algorithm on a hypergraph structure to represent this SAS space. For efficiency, it implements a dynamic Array/Sorted linked-list to guarantee the existance of a maximal probability projection of the hypergraph is always available. This combination of techniques results in several favorable planning and problem-solvign features, including stochastic error tolerance, the absence of need for a reward function, rapid learning rates, computational efficiency, input abstraction compatibility, and, naturally, agnosticism of training to the selected goal state. Further, its structure allows direct mathematical modeling which allows all these properties to be proved from theoretical analysis.

This repository contains a library implementing the GAP algorithm, pDij_type2.py, as well as several different test suites. These tests implement GAP learning on several problems of varying and adjustable levels of complexity, and are the tests which underwrite the data and analysis within the, also attached, paper "Goal Agnostic Learning and Planning without Reward Functions". This paper describes the algorithm mathematical analysis thereof, experimental validation, and additional modifications for training and implementation in exacting detail, and is the primary reference for the algorithm.

The descriptions below are, therefor, high-level overviews.

<h3>Mechanisms</h3>

<h3>Features</h3>

<h3></h3>

<h3></h3>

<h3></h3>









