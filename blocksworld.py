###
#
# Blocksworld Problem
#
#  Example of the GAP algorithm solving the blocksworld problem
#  Illustrates the GAP algorithm solving the dynamic free sorting problem,
#  especially with the possibility of multiple goal states, all viable
#  in parallel (indicating a lack of need for retraining or special training
#  for searching new goals).
#
#  This experiment incorporates an undirected explore phase for unsupervised
#  training
#
###

#Standards
import math,time,random

#For linear algebra
import numpy as np

#For file handling
import copy,pickle

#Import GAP algorithm agent
import pDIJ_type2 

class sim:
    #Class implementing the blockworld universe

    def __init__(self,_N):
        #initialize the world with the number of blocks, and bins for them
        self.N = _N
        self.bins = [[]]*4
        for i in range(self.N): #For each block
            j = random.randint(0,3) #Assign it a random bin
            self.bins[j] = self.bins[j] + [i] #Add it to the bin

    def move(self,i,j):
        #Method to move a block from bin i to j
        if self.bins[i] != []: #If not from an empty bin
            self.bins[j] = self.bins[j] + [self.bins[i][-1]] #Pop the top block off the stack and onto the other one
            self.bins[i] = self.bins[i][:-1]
        else:
            return -1 #If it's empty, return that you can't move anything

    def do_action(self,act):
        #Wrapper to convert an action index into a movement
        j = act%4 #Stride indexed as to + 4*from
        i = int((act - j)/4)
        self.move(i,j) #do the movement

    def state_make(self):
        #Function to convert the bins into a state
        state = str(self.bins)
        return state

    def state_make_2(self):
        #Another state function, more abstracted
        s1 = [len(a) for a in self.bins] #Get the bin lengths
        s2 = [] #empty list
        for a in self.bins: #For each bin,
            if a != []: #If not empty
                s2 = s2 + [a[-1]] #put the top block into s2
            else: #if empty
                s2 = s2 + [-1] #put -1 into s2

        # Three options: 
        #return str(s1)+","+str(s2) #lengths plus top block
        return str(s1) #Just lengths- turns out this is enough! Neat, right?
        #return str(s2) #just top blocks

    def is_goal(self):
        #Method to determine if we're possibly in a goal state 
        if max([len(a) for a in self.bins])==N:
            return 1
        else:
            return 0

#Main test
# P_thresh is the probability of an induced error in the action space
for P_thresh in [0.0,0.1,0.2,0.3]: #0% to 30% error induction
    for N in [3,4,5,6]: #For 3 to 6 blocks

        print("N = ",N," Pt = ",P_thresh," : ****") #Note the test block

        #Running 100 trials of 30 epochs each
        trials = 100
        epochs = 30
        trial_dat = [0]*epochs #final data

        #Looping over each trial
        for t in range(trials):

            #Create a new GAP agent
            brain = pDIJ_type2.pDIJ_type2(N**4,16,0.05,30,35)

            #Optional load previously trained brain
            #brain = pickle.load(open("bsw_brn_1.p","rb"))

            #Complex goal state- blocks sorted
            g = [a for a in range(N)]

            #Create a new blocksworld instance
            t_world = sim(N)

            #Construct all complex goal states- sorted in any bin
            goals = [[]]*4
            for a in range(len(goals)): #loop over each goal
                goals[a] =  goals[a] + [[]]*4 #Add a new set of bins
                goals[a][a] = g #put the basic goal arrangement into the ath bin
                t_world.bins = goals[a] #add the state into the world
                goals[a] = t_world.state_make_2() #grab the actual state that would be printed as

            #Add all the goal states as reachable entries to the brain
            for g in goals:
                brain.add_state(g)

            #Data for output
            dats = []

            #Looping over the testing eopchs
            for a in range(epochs):
                stg = 0 #current steps-to-goal
                world = sim(N) #Make a fresh simulation

                #While not at a goal state
                while not(world.is_goal()):
                    si =  world.state_make_2() #make the current state
                    brain.add_state(si) #Add state (brain handles it if already seen)

                    opts = [] #optional actions to take
                    if a > 1: #if not in the first two trials (the explore phase)
                        for g in goals: #for each goal option
                            acts,path = brain.find_path_native(si,g) #Find action sequence to goal
                            if acts != -1: #If a path found
                                opts = opts + [(acts,path,len(acts))] #Add it to options
                    else:
                        opts = [] #If first two epochs, don't search paths

                    #If there's options, and we're not at a random error
                    if opts != [] and random.random() > P_thresh:
                        opts.sort(key=lambda op:op[2]) #sort options by probability
                        act = int(opts[0][0][0]) #pick most probable
                    else: #If in explore 
                        #act = random.randint(0,world.N**2-1) #random action in all possibilities
                        act = random.randint(0,15) #partial action space- induced bias, too

                    world.do_action(act) #Take the action selected

                    sf = world.state_make_2() #Get resulting state
                    brain.add_state(sf) #Add state
                    brain.update_native(si,sf,act) #Update learning

                    stg+=1 #increase steps-to-goal

                    if stg%1000 == 0: #Every 1000 steps, print diagnostics
                        print(stg,[len(b) for b in world.bins])

                #Optional epoch prints
                #print(a,stg)
                #print("--------")
                dats = dats + [stg] #Update training data

            #For all training data in this experiment
            for a in range(len(dats)):
                trial_dat[a] = trial_dat[a] + dats[a] #Add to overall trial data
                #print(a,dats[a]) #Optional display
            #print(t,*"********") #Spacer for per experiment data visibility

        #Output the results of full experiments
        for a in range(len(trial_dat)):
            print(a+1,trial_dat[a]/trials) #Print the experiment number and amortized stg
        print("********")

    









