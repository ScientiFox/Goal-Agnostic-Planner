<img width="2776" height="1856" alt="GAP digest" src="https://github.com/user-attachments/assets/70d17bf5-a66d-4c5f-bc38-d010ff007cd6" />

<h2>Goal Agnostic Planning Algorithm</h2>

The Goal Agnostic Planner, or GAP, algorithm is a hybrid fusion of classical AI techniques for problem solving and machine learning concepts derived from reinforcement learning and probabilistic inference. It implements a State/Action/State model for learning, with a likelihood-maximization implementation of Dijkstra's algorithm on a hypergraph structure to represent this SAS space. For efficiency, it implements a dynamic Array/Sorted linked-list to guarantee the existance of a maximal probability projection of the hypergraph is always available. This combination of techniques results in several favorable planning and problem-solvign features, including stochastic error tolerance, the absence of need for a reward function, rapid learning rates, computational efficiency, input abstraction compatibility, and, naturally, agnosticism of training to the selected goal state. Further, its structure allows direct mathematical modeling which allows all these properties to be proved from theoretical analysis.

This repository contains a library implementing the GAP algorithm, pDij_type2.py, as well as several different test suites. These tests implement GAP learning on several problems of varying and adjustable levels of complexity, and are the tests which underwrite the data and analysis within the, also attached, paper "Goal Agnostic Learning and Planning without Reward Functions" (available here: https://www.oajaiml.com/uploads/archivepdf/97911150.pdf). This paper describes the algorithm mathematical analysis thereof, experimental validation, and additional modifications for training and implementation in exacting detail, and is the primary reference for the algorithm.

The descriptions below are, therefor, high-level overviews.

<h3>Mechanisms</h3>
There are three primary components which comprise the GAP algorithm, and underwrite its efficacy, Dijkstra's algorithm for maximum-likelihood path planning, the State/Action/State hypergraph, and Sorted Array/Linked-lists.

- _State/Action/State Hybergraph_: This learning model records instances of actions causing transitions between states. Because it is presumed that many actions can be taken from a given state, and each action may have more than onr result, depending on conditions, this structure represents a hypergraph instead of a standard graph.

<img width="481" height="176" alt="image" src="https://github.com/user-attachments/assets/853d8250-af25-469b-9af6-67c0aae83f40" />

- _Dijkstra's Algorithm for Maximum-likelihood path planning_: This application treats the action mediated transitions between actions as probabilistic, and uses joint probability maximization as the measure for identification of an optimal path, defined by the actions most likely to effect any given state transition.

<img width="423" height="285" alt="image" src="https://github.com/user-attachments/assets/a8bdc364-2c0a-42c2-b19d-45d4ba4c2e81" />


- _Array/Sorted Linked Lists_: This data structure represents the SAS hypergraph as a collection of array-indexed sorted linked lists, allowing reflexive referencing between SAS triplets and making a maximum-probability graph slice of the hypergraph always available.

<img width="618" height="470" alt="image" src="https://github.com/user-attachments/assets/f8d4e021-8550-4217-99bf-ab80b79fb916" />


<h3>Features</h3>

 - _Lack of Reward Function_: Because the SAS model collects observed and prompted information- actions taken by the agent, and operates entirely on probabilities derived from these instance counts, no reward function is required to train GAP agents when maximizing probability or minimizing steps-to-goal. This makes the agent free of the bias and risk of poor design of an objective function. However, the algorithm can be used with costs, such as minimum expectation of cose (probability and cost in tandem), energy, time, or similar.

<img width="459" height="80" alt="image" src="https://github.com/user-attachments/assets/e709c9ef-07c3-4f4a-b320-e776bf134776" />

 - _Goal Agnosticism_: Because the algorithm's model counts SAS transitions, all such can be used to determine paths between any observed, non-disjoint states. As such, while we often specify a goal for termination of epochs, any reachable state can be sought using the same training data. Notably, this information (states and actions) requires no further input than standard SA model learners

<img width="225" height="57" alt="image" src="https://github.com/user-attachments/assets/111b111d-715b-4d43-98c4-236d06ffb514" />
 
 - _Optimality_: Addressed in detail in section **4.1 Optimality of GAP plans** in the attached paper, the combination of embedding optimality of the Array/Linked-lists and Dijkstra's algorithm ensures that plans produced by the GAP algorithm are stochastically optimal.

<img width="336" height="100" alt="image" src="https://github.com/user-attachments/assets/b234705f-956c-4327-9e9e-c04a9cda4a6d" />

 - _Bounded Time Performance_: Addressed in detail in section _4.2.3 Derivation of Bounded Time Performance_
 in the attached paper, the Sequence Inference algorithm remits to analysis of the choice sequences of the agent as a MDP, from which demonstrates the probability of the system reaching the goal state increasing exponentially.

<img width="314" height="53" alt="image" src="https://github.com/user-attachments/assets/10601fad-3bf8-4392-8e94-54291529d1af" />

 - _Computational Efficiency_: Addressed in sections **3.3 Subgraph Maintenence Algorithm** and **3.4 Sequence Inference Algorithm**, the maintenance of the SAS hypergraph and maximal likelihood slide are constant bounded, and the inference algorithm is bounded in quadratic time, ensuring low-order polynomial computation time.

 - _Robustness to Error_: Addressed in detail in section **4.3 Analysis of Robustness under perturbation** the agent's dynamics under the MDP model can be used to hypothesize a further transfer function representing perturbations of the system, and goal convergance can be shown to hold under broad conditions.

<img width="716" height="62" alt="image" src="https://github.com/user-attachments/assets/8b951ac8-fb5c-40d6-b4e1-a3d1c1de90f0" />

 - _Abstraction Tolerance_: Addressed in section **4.4 Impact of Perturbed State on Performance**, the transfer functions previously mentioned can also be used examine state abstraction models on performance, and an exponential bounding measure for such derived, indicating tolerance of relatively aggressive abstractions.

<img width="273" height="56" alt="image" src="https://github.com/user-attachments/assets/ac27913b-a287-49c3-8543-bb92d3a8d1c9" />

 - _Reciprocal Convergence_: Addressed in section **4.5 Learning Convergence**, using the same mechanism used for error and abstraction analysis, the agent's learning is modeled as a progressively improving error mask, and goal convergence rates are shown to be statistically reciprocal as learning progresses.

<img width="231" height="50" alt="image" src="https://github.com/user-attachments/assets/07b2db39-920a-4641-8881-59fac24e346c" />
   
<h3>Examples</h3>

<img width="734" height="166" alt="image" src="https://github.com/user-attachments/assets/716f5f5b-5f98-4323-8033-27112d59d898" />

- _Strips-type Problems_: Learning a problem form typical of traditional hierarchical AI planners, to demonstrate essential functionality of the algorithm. Additionally includes the injection of random error to illustrate robustness to these deviations. These tests demonstrate strong agreement with the reciprocal learning pattern postulated by theory, as well as the exponential bounding on error tolerance. (Section **5.2 STRIPS-type Problems**)

<img width="678" height="374" alt="image" src="https://github.com/user-attachments/assets/e004f54f-5bf9-443b-8132-899a1c174789" />

<hr>

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/edcedfd7-9756-4ef8-8955-4fa47276d316" />

- _TAXI and MAZE Problems_: Learning a problem which is a hierarchical hybrid of the TAXI problem (navigating to passengers and transporting them to destinations with obstacles) and MAZE problems (successfully navigating within a highly nonlinear space). Examinations of low complexity mazes (obstacles) and high complexity mazes (actual mazes and poorly conditioned ones) demonstrate the same reciprocal learning law, functionality under state abstractions, hierarchical learning, error robustness, the abstraction quality metric, and relativistic state learning- the mazes are randomly generated and learning is local. The agent does not learn _a_ maze, it learns maze navigation based on local features. (Section **5.3 Maze/TAXI Domain**)

<img width="768" height="344" alt="image" src="https://github.com/user-attachments/assets/5de6b315-c6ac-4865-9f7e-fc72cedfb85a" />

<hr>

<img width="457" height="133" alt="image" src="https://github.com/user-attachments/assets/37f7b83f-6796-47dc-bbe8-fb0491b88078" />

- _Tower of Hanoi Puzzle_: Learning to solve the Tower of Hanoi puzzle, another hierarchical problem, but with more rigid state space and a wider action space than previous problems. Demonstrates continued fit of the reciprocal learning law, error robustness, abstraction tolerance, providing analysis over increasing complexity space responses, and validating the relation between error and abstraction budgets on performance. (Section **5.4 Tower of Hanoi Domain**)

<img width="619" height="343" alt="image" src="https://github.com/user-attachments/assets/0bd349a4-b3a2-4b8d-a132-d457499527b5" />

<hr>

<img width="190" height="107" alt="image" src="https://github.com/user-attachments/assets/96e9b92b-ab8a-4400-80aa-81b64be8acc2" />

- _Blocksworld Problem_: A simple sorting problem, similar to that of the Tower of Hanoi, but with fewer state space restrictions, and constining the Sussman Anomaly as a sub-problem. Demonstrates acutely rapid training and avoidance of the Sussman anomaly. (Section **B.1 Blocksworld**)

<img width="814" height="398" alt="image" src="https://github.com/user-attachments/assets/b7cd6a6e-7d86-4fd4-911d-87c5c47a5a26" />

<hr>

<img width="182" height="179" alt="image" src="https://github.com/user-attachments/assets/941e9df6-4a14-49d2-b94f-9d4a2346e6ad" />

- _Binary Addition Problem_: Another simple problem, learning to add together binary digits correctly. Also demonstrates very rapid learning, and in this case on another fully relative problem- the agent has a bit setting, carry bit value, and a pointer increment function, it does not operate over bit-length digits. (Section **B.2 Binary Addition**)

<img width="604" height="334" alt="image" src="https://github.com/user-attachments/assets/8c65b813-2a9e-458c-a1c9-722ec02b1862" />

<h3>Algorithm Augmentations</h3>

In addition to the basic features and examples outlined here, there are also several augmentations which we have experimented with on the GAP algorithm. Some are addressed in experiments in the repository, as well as discussed in the pertinent sections in the paper, or in **Appendix A. GAP Algorithm Modifications**. We overview these here, too.

- _Implicit learning rate_: The GAP algorithm does not have an explicit learning rate as a parameter which can be set, but it is possible to alter the time sensitivty of learning by the inclusion of an approximation of a moving average window, the width of which is an approximant of a learning rate

<img width="195" height="66" alt="image" src="https://github.com/user-attachments/assets/3e54e6e8-82f3-4443-8fa6-213ec1fe9a6a" />

- _Alternative choice planning_: The core GAP algorithm assumes action selection is made by picking the next action in the maximum likelihood chain between the current state and the goal. An alternative used in amny ML systems, selecting actions probabilistically, weighted by quality or probability of success, can also be applied, though it effects a shift in the explore/exploit behavior of the system.

<img width="605" height="111" alt="image" src="https://github.com/user-attachments/assets/d853a8d9-80d0-4a72-9b42-9682628b0d53" />

- _In-situ transfer functions_: An alternative to learning an entire hypergraph of transitions is to supply a subset of transitions ahead of time, either as a partial hypergraph or as a direct calculation function. This would model remaining, learning-oriented segments of the graph as smaller learning problems, with the expected attendant rate benefits, as well as additional certainty in transition probabilities, albeit at risk of bias.

<img width="617" height="121" alt="image" src="https://github.com/user-attachments/assets/30f53422-1511-4244-8f74-5c0cc8bc6ad0" />

- _Generalized A* heuristics_: Given that we use Dijkstra's algorithm as the core of the inference mechanism, it stands to reason that A* would have superior performance. Although introducing an external heuristic is an opportunity to introduce bias, and is an influence similar to a quality function, section **A.4 Generalized Heuristics for A\*** discusses the possibility of structurally-based heuristics which do not present this risk, and are similar to learning re-use. 

<img width="355" height="176" alt="image" src="https://github.com/user-attachments/assets/630ed14e-a0f9-4046-b28b-951fc6f3aa34" />

- _Augmented states_: Similar to the mechanism of temporal chaining in the Murin project, it is possible to use prior-state and prior-action based vector augmentations as input states for GAP algorithms, modelable as another form of state abstraction. Although less of a dramatic learning and capability boost for GAP, which already includes a temporal mechanism, experiments with the Tower of Hanoi and TAXI/MAZE problems include successful explorations of this. 

- _Tabu search training_: Because the GAP agents must spend at least a small initial portion of training exploring purely, when they don't have a sufficiently developed hypergraph to locate the goal state they seek, it is critical that search be as maximall spanning as possible. A technique we apply in the STRIPS, TAXI/MAZE, and Tower of Hanoi problems, all, is a Tabu table- the agent keeps a running list of state/action pairs, and in any state where it cannot find a path to a goal, picks actions instead by uniform sampling across the Tabu table, which is highly effective for initial phases.

- _Replanning_: Because the GAP algorithm is fully goal independent and also de-facto start state independent, we automatically have subproblem optimality. Because of this, we can assume that, when slipping off the optimal path because of stochastic factors, the planning from the current state  As a result, if taking the overlap of all prior solutions found, we need only plan to reach a state previously planned for, and the plan from there remains valid, as if we had observed an instance that would change that plan, the planning would necessarily have preceeded that state

