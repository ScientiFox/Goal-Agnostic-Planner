###
#STRIPS type problem 
#
# A problem in the style of traditional, hierarchical
#  planning problems for classical AI systems to solve
#
# Problem elements are:
#  Location types:
#  Space - just links: [L1,L2,L3...]
#  Door - 2 links, only traversable if open (DS=1): [LA,LB]
#  Vending Machine - 1 Link, can get soda: [L]
###

#Standards
import math,time,random

#For linear algebra
import numpy as np

#Import GAP algorithm agent
import pDIJ_type2

class place:
    #Object for places in the world model

    def __init__(self,Name,Type,State):
        #Initialize room with name and type
        self.Name = Name
        if Type in ['Space','Door','Vending Machine']: #Specific types for the room cell
            self.Type = Type
        else:
            return -1 #Fail if not a legitimate type
        self.Links = []
        self.State = State #Initial state

    def add_links(self,links):
        #Wrapper to update the link set
        self.Links = self.Links + links
        return 1

    def set_state(self,state):
        #Wrapper to assign an internal state for the object
        if len(state) == len(self.State):
            self.State = state
            return 1
        else:
            return -1

    def get_type(self):
        #Wrapper to get the room's type
        if self.type == 'Space':
            return 0
        elif self.type == 'Door':
            return 1
        elif self.type == 'Vending Machine':
            return 2
        else:
            return -1

    def activate(self):
        #Activate function to toggle state of a place, dependent on the type
        if self.Type == 'Door':
            self.State[0] = 1 - self.State[0]
            return 1,"None"
        if self.Type == 'Vending Machine':
            return 2,"Soda"
        else:
            return -1,"None"

    def __str__(self):
        #Print function
        return self.Name

class Agent:
    #Class for an agent's state set in the world model

    def __init__(self,location):
        self.location = location #Location of the agent (a place object)
        self.items = [] #Items collected
        self.location_dict = {location:0} #Set of locations observed with encoding
        self.locations = 1 #Number of observed locations for encoding

    def get_directions(self):
        #Get the list of places the agent can go
        return len(self.location.Links)

    def get_destinations(self):
        #Get names of the places linked to the current location
        return [a.Name for a in self.location.Links]

    def print_loc_dict(self):
        #Print out the list of encoded places observed
        for a in self.location_dict:
            print(a.Name," ",self.location_dict[a])

    def move(self,direction):
        #Method to move the agent in the world

        #If the direction is to a viable direction
        if direction < len(self.location.Links):
            #If the type of room is traversable
            if (self.location.Type != "Door") or (self.location.State[0] == 1) or (self.location.Links[direction] == self.location.State[1]):
                #if going to a door
                if self.location.Links[direction].Type == "Door":
                    self.location.Links[direction].State[1] = self.location #Move to the door
                self.location = self.location.Links[direction]  #grab new location
                if not(self.location in self.location_dict): #If a new location
                    self.location_dict[self.location] = self.locations #Add index to the map
                    self.locations+=1 #Increase the count of locations
                return 1
            else: #If not a traversible location, return failure
                return -1
        #If the direction is invalid, return failure
        else:
            return -1

    def activate(self):
        #agent's activate- calls the place's activate and processes results
        code,item = self.location.activate()  #Grab activation from location
        if item != "None" and not(item in self.items): #If not nothing returned and you don't have the item
            self.items.append(item) #Add the item to the possessions
        return code #return the code for what happened

    def print_surroundings(self,mode):
        #Function to pretty print the agent's current surroundings
        print(self.location.Name,self.location.Type)
        if mode > 0:
            print("   ",[str(a) for a in self.location.State],self.items)
        elif mode > 1:
            print([a.Name for a in self.location.Links])

def print_world(world):
    #Function to pretty print the state of the world model
    for a in world:
        print(a.Name," ",a.Type)
        print("----")
        print("    ",)
        for b in a.Links:
            print(b.Name," ",)
        print(" ")
        print("----")

def state_make(agent):
    #function to return a world state for the agent learner
    return agent.location.Name+str([str(a) for a in agent.location.State])+str(agent.items)

def take_action(agent,act):
    #Function to process an action taken by the agent
    if act in range(4): #If a move action
        if (random.random() > ERROR): #Injected error
            agent.move(act) #do the movement if not in an artificial error
        else: #Otherwise
            agent.move((act+random.randint(0,3))%4) #do a random movement
    else: #if not a movement
        if (random.random() > ERROR): #if not injected error
            agent.activate() #do the activation

def print_S2E(S2E):
    #Wrapper to print a state to action mapping
    for a in S2E:
        print(a,S2E[a])

#Make the places
L1 = place("L1","Space",[])
L2 = place("L2","Space",[])
L3 = place("L3","Space",[])
L4 = place("L4","Space",[])
L5 = place("L5","Space",[])
L6 = place("L6","Space",[])
L7 = place("L7","Space",[])
L8 = place("L8","Space",[])
L9 = place("L9","Space",[])
L10 = place("L10","Space",[])
L11 = place("L11","Space",[])
D1 = place("D1","Door",[0,0])
V1 = place("V1","Vending Machine",[])

#Link the places together
L1.add_links([L2,L4,L5])
L2.add_links([L1,L3])
L3.add_links([L4,L2])
L4.add_links([L5,L1,L3])
L5.add_links([D1,L1,L4])
L6.add_links([D1,L8,L7])
L7.add_links([L6,L8,L10])
L8.add_links([L6,L7,L9])
L9.add_links([L8,L10,L11])
L10.add_links([L7,L9,L11])
L11.add_links([L9,L10,V1])

#Add the door links
D1.add_links([L6,L5])

#Add the vending mahcine links
V1.add_links([L11])

#environment to abstract states:
#Env : (place,state)
E2S = {} #environment to state
S2E = {} #state to environment

# Different error injections for stochastic testing
#ERROR = 0.3
#ERRORS = [0.0,0.01,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7]
#ERRORS = [0.02*a for a in range(30)]
ERRORS = [0.30]

#epoch values
X = 20 #number of slots for experiments 
EPs = 100 #number of epochs

#Output data string for final data write
OUT_STRS = [""]*(EPs+1)

for ERROR in ERRORS :#for each error level being tested

    explrs = [4]*X #list of exploration phases for each experiment
    exp = -1 #explore flag

    Vals = []

    #Populate dictionary of environment states- for diagnostic overview
    agentL =  Agent(L2) #make an agent
    for b in range(3000): #for 3000 trials
        take_action(agentL,random.randint(0,4)) #take a random action
        if not(state_make(agentL) in E2S): #if the state hasn't been seen
                StrS = state_make(agentL) #make the state
                i = len(E2S) #make an index from the string state's length
                E2S[StrS] = i #build the reflexive lookups for states and indices
                S2E[i] = StrS

    #Looping ovver the number of experiments
    for b in range(X):

        #Make a new brain
        Brain = pDIJ_type2.pDIJ_type2(50,5,0.05,15,20)

        vs = [] #data values

        for a in range(EPs): #looping over the number of epochs

            #make an interaction agent
            agent =  Agent(L2)
            for c in range(10): #take random actions to make the start state for learning random
                take_action(agent,random.randint(0,4))
            D1.set_state([0,0]) #Set the door state fresh if passed through it
            goal = "L2[]['Soda']"  #set the goal to be bringing soda to a known location

            #check if the current state hasn't been seen
            if not(state_make(agent) in E2S):
                StrS = state_make(agent) #if not make the state
                i = len(E2S) #and add it to the lookup
                E2S[StrS] = i
                S2E[i] = StrS

            #counter 
            cntr = 0
            
            while (state_make(agent) != goal): #until reaching the goal

                #If out of the explore phase
                if (a > exp):
                    #Try and find an action sequence solution
                    As,Ps = Brain.find_path(int(E2S[state_make(agent)]),int(E2S[goal]))
                    if As == -1: #if no path found
                        act_r = random.randint(0,4) #random action
                        s_n = -2 #operational state flag for diagnostics
                    else:
                        act_r = int(As[0]) #otherwise grab first action
                        s_n = int(Ps[1]) #operational state flag for diagnostics
                else:
                    act_r = random.randint(0,4) #if exploring still- random action
                    s_n = -2 #operational state flag for diagnostics

                #make the agent's initial state for training
                s_p = E2S[state_make(agent)]

                #take selected action
                take_action(agent,act_r)

                #Add the new state if not already seen
                if not(state_make(agent) in E2S):
                    StrS = state_make(agent) #same as before
                    i = len(E2S)
                    E2S[StrS] = i
                    S2E[i] = StrS

                #Optional progress diagnostic
                #if cntr > 5000:
                #    print(int(s_p),s_n,int(E2S[state_make(agent)]),int(act_r),Brain.AF[1,int(s_p),int(s_n)])

                #train the brain on prior state, current state, and selected action
                Brain.update(int(s_p),int(E2S[state_make(agent)]),int(act_r))
                cntr+=1 #increment the steps counter

            # Option to write an image of the compressed max-probability brain array
            #cv2.imwrite("data.png",Brain.AF[1,:,:]*255)

            # Option to print the post-epoch data
            #print(a,cntr)

            vs = vs + [(a,cntr)] #Add epoch and steps-to-goal to the output data

            # Option to print the final maximum-likelihood path
            #print Brain.find_path(int(E2S[state_make(agent)]),int(E2S[goal]))
            #print "--------"

        #Add epochs data from this experiment to total data
        Vals = Vals + [vs]

        # Optional output of brain max prob from last run
        #cv2.imwrite("data.png",Brain.AF[1,:,:]*255)

    #Array for averages over all experiments
    avgVals = [0]*EPs

    #looping over data from each experiment
    for a in Vals:
        n = 0 #position index
        for b in a: #looping over all date from each epoch in this experiment
            avgVals[n] = avgVals[n] + b[1]/(1.0*X) #average across epoch numbers for all experiments
            n+=1 #increment index number

    #Print some space and the error level being tested
    print("")
    print("")
    print(str(ERROR) + ": --------")
    OUT_STRS[-1] = OUT_STRS[-1] + str(ERROR) + ", " #Add error label to output string

    #Looping over epoch-averaged steps-to-goal for this experiment
    for a in range(len(avgVals)):
        OUT_STRS[a] = OUT_STRS[a] + str(round(avgVals[a],1)) + ", " #Add average STG for this experiment to output strings
        print(avgVals[a])#print results

#At end of all experiments
for a in OUT_STRS:
    print(a) #print all finalized data for review





