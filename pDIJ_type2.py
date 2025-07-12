# pDIJ Type-2 revision

import math,time,random
import numpy as np

class LL:
    #Linked list class implementation
    #   mainly a tidy wrapper to enforce relationships (order/push/pop/remove only)

    def __init__(self):
        #list and length- len() felt messy
        self.lit = []
        self.len = 0

    def push(self,value):
        #Add one value to the front of the list
        if value != None:
            self.lit = [value] + self.lit
            self.len = self.len + 1
        else:
            return kl

    def pop(self):
        #Pop a value off the top of the list
        if self.len > 0:
            #Pull off the list destructively
            val = self.lit[0]
            self.lit = self.lit[1:]
            self.len = self.len - 1
            return val
        else:
            #Nothing if the list is empty
            return None

    def remove(self,val):
        #Pull a specific value from the middle of the list
        popd = -1
        store = LL() #Stack to store previously checked values
        while (popd != val) and (self.len != 0): #pull values off until you find ti
            popd = self.pop()
            if popd != val:
                store.push(popd)
        while store.len != 0: #Put everything back
            self.push(store.pop())

    def __str__(self):
        #A string output for display
        return str(self.lit)

class LLA:
    #Linked-list array object

    def __init__(self,_S,_A):
        #Init with S/A for width and depths
        self.S = _S
        self.A = _A
        self.array = [LL() for a in range(self.S*self.A)] #An LL for each array cell

    def __getitem__(self,t):
        #fetch method
        si,ak = t
        i = si*self.A + ak
        return self.array[int(i)]

    def __setitem__(self,t,lit):
        #Set method
        si,ak = t
        i = si*self.A + ak
        self.array[int(i)] = lit


class pDIJ_type2:
    #Probabilistic implementation of Dijkstra's algorithm on ALL datastructures

    def __init__(self,_S,_A,_P,_cR,_cT):
        #Initialize state space size and action space size
        self.S = _S
        self.A = _A

        #Lookup tables for string formatted state inputs
        self.E2S = {} #Environment (string) to state (index)
        self.S2E = {} #State (index) to Environment (string)
        self.En = 0 #Size of lookup table

        #State visit counter for Tabu exploration
        self.visit = [0]*self.S
        self.visit[0] = 1 #Initial state- 1st observation
        self.visits = 1 #Total number of visits

        # Edge removal min connection - least probability to be considered a fluke
        self.P_thresh = _P

        # Count magnitude learning rate
        self.cnt_reset = _cR #number of observations to pin as max
        self.cnt_thresh = _cT #number of observations to trigger a re-scale at

        # Root incrementor array
        self.INC = np.zeros((self.A,self.S,self.S))  #Counts of all events
        self.INC_sum = 0 #Total number of observations

        # Array tracking |a_i(s_j) -> s_x|
        #   AK[ak,si] = |a_i(s_j)| 
        self.AK = np.zeros((self.S,self.A))

        # Array tracking a_x(s_j) -> s_k
        #   Tracks which action causes s_j->s_k most
        #   reliably based on AK.
        self.AF = np.zeros((2,self.S,self.S))
        self.AF[0,:,:] = -1*np.ones((self.S,self.S))
        # [a_?,P_?jk]

        #Array linked list object
        ###
        # ^linked list array LLA indexed in
        #  [s_i,a_k] which contains for each the list of
        #  s_f for which a_k is the most likely transition
        #  These are linked lists embedded within the array
        #  and maintained in sorted order all the time (see below)
        ###
        self.AL = LLA(self.S,self.A)

        # Populate ALL w/ initial link objects
        for si in range(self.S):
            for sf in range(self.S):
                akf = random.randint(0,self.A-1) #Initial random 'most likely' action
                self.AL[si,akf].push(sf)
                self.AF[0,si,sf] = akf

        #Adjacenct map- initially empty
        self.adjacency = [[]]*self.S #Adjacency lists
        self.adj = -1*np.ones((self.S,self.S)) #Flag map for adjacency checks

        #Containers for prior actions and plan trees
        self.last_tree = -1
        self.d_m_list = -1
        self.last_plan = [-1],[-1]
        self.last_goal = -1

    def add_state(self, Es):
        #Method to add a new state on discovery

        #If the state is actually new
        if not(Es in self.E2S):
            self.E2S[Es] = self.En #Add new index
            self.S2E[self.En] = Es #Add new environmental state
            self.En = self.En + 1 #Increment state counter

            self.visit = self.visit + [1] #Add a new cell to the states-visited list

            #If adding that new state increased the number of states over the array size
            if self.En > self.S:

                #Build and populate the new AF array
                AF_p = np.zeros((2,self.S+1,self.S+1))
                AF_p[0,:,:] = -1*np.ones((self.S+1,self.S+1))
                AF_p[:,:-1,:-1] = self.AF
                self.AF = AF_p

                #Augment the main ALL object
                self.AL.S = self.AL.S + 1
                self.AL.array = self.AL.array + [LL() for a in range(self.A)]

                #Add in new random first actions to the additional array space
                for sf in range(self.S+1):
                    akf = random.randint(0,self.A-1)
                    self.AL[self.S,akf].push(sf)
                    self.AF[0,self.S,sf] = akf

                #Expand the AK array
                AK_p = np.zeros((self.S+1,self.A))
                AK_p[:-1,:] = self.AK
                self.AK = AK_p

                #Expand the incrementor
                INC_p = np.zeros((self.A,self.S+1,self.S+1))
                INC_p[:,:-1,:-1] = self.INC
                self.INC = INC_p

                #Augment the adjacency list and map
                self.adjacency = self.adjacency + [[]]
                adj_p = -1*np.ones((self.S+1,self.S+1))
                adj_p[:-1,:-1] = self.adj
                self.adj = adj_p

                #Increase the size of the statespace
                self.S = self.S + 1
            return True

        #If it's not actually new, skip all that
        else:
            return False

    def make_state(self, Es):
        #Get the state index from the lookup table
        return self.E2S[Es]

    def update_native(self,si_e,sf_e,ak):
        #Perform an update of the agent's model using the environmental states

        #Ensure the states are in the lookup tables
        self.add_state(si_e)
        self.add_state(sf_e)

        #Grab their indices
        si = self.E2S[si_e]
        sf = self.E2S[sf_e]

        #do the index-based update
        self.update(si,sf,ak)
        
    def update(self,si,sf,ak):
        #Index based update of the agent model

        #Update the incrementor counter
        self.INC[ak,si,sf] = self.INC[ak,si,sf] + 1
        self.INC_sum = self.INC_sum + 1

        #Update the AK counter
        self.AK[si,ak] = self.AK[si,ak] + 1

        #Update the Tabu visit list
        self.visit[sf] = self.visit[sf] + 1
        self.visits = self.visits + 1

        #Calculate the updated probability
        P_n = self.INC[ak,si,sf]/self.AK[si,ak]

        #Check if the new probability is above the viable-edge threshold
        if self.adj[si,sf] == -1 and P_n > self.P_thresh:
            #If sufficiently likely to be a viable edge, mark adjacency
            self.adjacency[si] = self.adjacency[si] + [sf]
            self.adj[si,sf] = 0
        elif self.adj[si,sf] != -1 and P_n <= self.P_thresh:
            #Otherwise, remove from adjacency list
            self.adjacency[si].remove(sf)
            self.adj[si,sf] = -1

        #Check if updated probability is greater than current maximum
        if (P_n > self.AF[1,si,sf]):
            #if so, grab action associated with most-likely transition
            a_p = self.AF[0,si,sf]

            #Move the prior lead element back and the current one up to the front
            self.AL[si,a_p].remove(sf)
            self.AL[si,ak].push(sf)

            #update AF array indices with action and probability
            self.AF[0,si,sf] = ak
            self.AF[1,si,sf] = P_n

        #make a temporary stack
        store = LL()

        #empty prior ALL for this s/a pair
        while self.AL[si,ak].len != 0:
            #Pop each element
            sl = self.AL[si,ak].pop()
            as_Ps = self.INC[:,si,sl] #grab local slice of incrementor

            #O(1) w/ INC update above tracking argmax in ak dir.
            al_maxP = int(np.argmax(as_Ps)) #grab max probability element
            self.AF[0,si,sl] = al_maxP  #get the actual probability

            #If the AK component for that s/a pair is a real probability (observed)
            if self.AK[si,al_maxP] > 0:
                #update AF array with new peobability
                self.AF[1,si,sl] = as_Ps[al_maxP]/self.AK[si,al_maxP]

                #if the probability is less than the adjacency threshold
                if self.AF[1,si,sl] < self.P_thresh:
                    self.AF[0,si,sl] = -1 #Clear the action index flag
                    self.AF[1,si,sl] = 0.0 #Set effective probability to 0
                    try:
                        self.adjacency[si].remove(sl) #Remove the state if it's in the adjacency list
                        self.adj[si,sl] = -1 #clear the adjacency flag
                    except:
                        pass #Otherwise it's already not in there, ignore
            #If the ALL component is not observed
            else:
                self.AF[1,si,sl] = 0.0 #Set to 0 probability
                self.AF[0,si,sl] = -1 #Clear flag

            #If the max probability is not the listed max
            if al_maxP != ak:
                self.AL[si,al_maxP].push(sl) #Add the state to the ALL element at that cell
            else:
                store.push(sl) #otherwise put it on the temporary stack

        #Put the stack into the ALL
        self.AL[si,ak] = store

        # Corrective factor to keep new samples relevant
        #  This is basically a parameterization of learning rate
        if self.AK[si,ak] >= self.cnt_thresh: #If the count for this pair is past the threshold
            self.AK[si,ak] = self.cnt_reset #Rescale the counter to the reset value
            self.INC[ak,si,:] = self.INC[ak,si,:]*(1.0*self.cnt_reset/self.cnt_thresh) #Rescale the incrementor to the new count value

        return 1

    def check_prob(self,path):
        #A method to calculate the probability of completing a path

        #Base probability of 1.0
        P_joint = 1.0

        #for each step in the path
        for a in range(len(path)-1):
            P_joint = P_joint*self.AF[1,path[a],path[a+1]] #Cumulative probability
            if P_joint == 0.0: #Stop as soon as probability goes to 0
                return 0.0
        return P_joint

    def find_path_native(self,si_e,sg_e,_verbose=False):
        #Get most likely path using environmental states

        #grab indices from lookup tables
        si = self.E2S[si_e] 
        sg = self.E2S[sg_e]

        #Return path from index-based method
        return self.find_path(si,sg,verbose=_verbose)

    def find_path(self,si,sg,verbose=False):
        #Find the most probable path from si to sg

        #Replanning- if returning to prior plan after diversion, can re-use it
        if (sg in self.last_plan[1]) and (si in self.last_plan[1]): #If the goal and current state both in plan
            if (self.check_prob(self.last_plan[1]) > 0.0): #If the probability has not been reset to 0 by the diversion updates
                if (si == self.last_plan[1][0]): #If returned to the state from which the diversion occurred
                    return self.last_plan #Return the old plan
                else: #If on an non-prior state
                    #grab the index of the current state on the prior plan
                    si_index = max([i*(self.last_plan[1][i] == si) for i in range(len(self.last_plan[1]))])
                    #Return the portion of the plan corresponding to the current state and later
                    return self.last_plan[0][si_index:],self.last_plan[1][si_index:]

        #Check if there are known transitions from the current state
        if (self.adjacency[si] == []):
            self.last_plan = [-1],[-1] #if not- clear the plan, in unknown territory
            return -1,-1 #return flags for 'no path available'
        else: #Otherwise

            #Prepare a list of states reachable from the current one
            reachable = [0]*self.S
            neighs =  self.adjacency[si]+[] #Grab the list of neighbors

            #While there are paths to explore and the goal has not been found
            while len(neighs) != 0 and reachable[sg] == 0:
                reachable[neighs[0]] = 1 #Mark the next neighbor as reachable

                #Grab all the states reachable from that enighbor
                for n in self.adjacency[neighs[0]]:
                    if reachable[n] == 0: #If not already seen
                        neighs = neighs + [n] #Add to the neighbours list
                        reachable[n] = 1 #Mark as reachable now
                neighs = neighs[1:] #pop each neighbor as it's handled

            if reachable[sg] == 0: #If the goal is not reachable from the current state
                self.last_plan = [-1],[-1]
                return -1,-1 #Return no-plan-found 

        #Update the flags to the current agent goal (only if reachable)
        self.last_goal = sg

        #Grab the max prob and max action arrays for all s/s transitions
        maxP = self.AF[1,:,:]
        maxA = self.AF[0,:,:]

        #Prepare the empty max probability tree
        MPT = np.zeros((self.S,self.S))

        #Variables for Dijkstra's algorithm
        permanent = [-1]*self.S #Set of states with final paths found
        distances = [-1]*self.S #Distances from the initial state to each final state
        distances[si] = 0 #Distanct to the initial state
        d_max = -1 #maximum distance
        d_m_list = [] #list of states w/ current max distance
        boundary_list = [] #list of states on the tree boundary
        reachable = [si] #List of reached states

        #Initial setup for Dijkstra
        permanent[si] = None #No predecessor for the root state
        for sk in self.adjacency[si]: #For each state adjacent to the start
            if maxP[si,sk] > 0.0: #If there is a non-0 probability of transition
                boundary_list = boundary_list + [(si,maxP[si,sk],sk)] #Add to the initial boundary list
        boundary_list.sort(key=lambda get: get[1],reverse=True) #Sort the initial list by probability

        t1 = time.time() #For performance monitoring

        #While there are new states to evaluate
        while len(boundary_list) > 0:

            #Print size of boundary and reachable set every 4 seconds (diagnostic)
            if time.time()-t1 > 4.0:
                print(len(boundary_list),len(reachable))

            #Strip off already-visited states from the boundary list
            while len(boundary_list)>0 and permanent[boundary_list[0][2]] != -1:
                del boundary_list[0]

            #If there are previously unseen states:
            if len(boundary_list) > 0:

                #Grab the first state off the queue
                add = boundary_list[0]
                del boundary_list[0]

                #Update the lists of permanent nodes and distances
                permanent[add[2]] = add[0]
                distances[add[2]] = distances[add[0]] + 1

                #If the current distance is greatest
                if distances[add[2]] > d_max:
                    d_max = distances[add[2]] #Set the new longest distance
                    d_m_list = [add[2]] #Set the list of max dist states to just this one
                elif distances[add[2]] == d_max: #If the same distance, add to the current list
                    d_m_list = d_m_list + [add[2]]
                reachable = reachable + [add[2]] #Annotate that this state is reachble
                MPT[add[0],add[2]] = add[1] #Add to the maximum probability tree

                new = [] #Holder list for the new boundary members

                #Grab all adjacent nodes and add to the boundary add-on list
                for sb in self.adjacency[add[2]]:
                    new = new + [(add[2],maxP[add[2],sb]*add[1],sb)]

                #Arrange new state list by probability
                new.sort(key=lambda get: get[1],reverse=True)

                #Insert into the boundary list
                n = 0
                while new != []: #While nodes to be added
                    #loop over nodes with higher probability
                    while n < len(boundary_list) and boundary_list[n][1] >= new[0][1]:
                        n+=1
                    #Insert most probable in new to place in boundary list
                    if n < len(boundary_list):
                        boundary_list = boundary_list[:n] + [new[0]] + boundary_list[n:]
                        del new[0]
                    else: #If at the end, add all that remain
                        boundary_list = boundary_list + new
                        new = []

        #Iterating backwards from the goal
        sk = permanent[sg] #Grab immediate predecessor state
        path = [sg] #'Start' list with goal
        acts = [] #No actions yet

        #Set note of prior tree & max distance list
        self.last_tree = (permanent + [],distances+[],reachable+[])
        self.d_m_list = d_m_list

        #If the goal has no parent in the tree, not path (should never get here with above checks, but for good measure & logical closure)
        if (sk == -1):
            self.last_plan = [-1],[-1]
            return -1,-1

        #If the goal has a parent, the path exists, get it
        else:
            #Until reaching the start state (predecessor of None)
            while (sk != None):
                path = [sk] + path #Add the current predecessor to the path
                acts = [maxA[path[0],path[1]]] + acts #Append the corresponding most-probable action
                sk = permanent[sk] #Grab the next predecessor

            #Set the most recent planned path to the one just found
            self.last_plan = acts,path
            return acts,path #Actually return the path



