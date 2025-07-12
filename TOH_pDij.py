###
# GAP simulation test, Tower of Hanoi Puzzle
#
#  GAP algorithm learningt o solve the Tower of Hanoi
#  puzzle, across multiple different problem scales, 
#  selected as combinations of numbers of rings and numbers
#  of pegs.
#
###

#Standards
import math,time,random

#For linear algebra
import numpy as np

#For file handling
import copy,pickle,cv2

#Import GAP algorithm agent
import pDIJ_type2

class TOH:
    #Tower of Hanoi puzzle object

    def __init__(self,_N,_T,_E):
        #Initialize key values
        self.N = _N # Number of disks
        self.T = _T + (3-_T)*(_T < 3) #Number of towers (must be >= 3)
        self.error = _E #Error rate
        self.stacks = [[i for i in range(self.N)]] + [[]]*(self.T-1) #Initial stack configuration
        self.act_p = 0 #previous action variable

    def move(self,i,f):
        #Method to move a disk from tower i to f

        #Set prior action to the current move
        self.act_p = self.to_a(i,f)

        #If the stack is empty, move is to the same tower, or either i or f is out of range
        if self.stacks[int(i)] == [] or (i<0)*(i>=self.T) or (f<0)*(f>=self.T) or (i == f):
            return -1 #Return no-move
        elif self.stacks[int(f)] == []: #If the destination stack is empty
            self.stacks[int(f)] = [self.stacks[int(i)][0]]  #Make the stack just the one moved disk
            self.stacks[int(i)] = self.stacks[int(i)][1:] #Remove the top disk from the 'from' tower
            return 1 #Return success
        elif self.stacks[int(f)][0] > self.stacks[int(i)][0]: #Otherwise, if the moved disk can go atop the destination tower
            self.stacks[int(f)] = [self.stacks[int(i)][0]] + self.stacks[int(f)] #Add it on top
            self.stacks[int(i)] = self.stacks[int(i)][1:] #Remove the disk from the from tower
            return 1 #Return success
        else: #If no move or exit condition satisfied
            return -1 #Return failure

    def to_a(self,x,y):
        #Convert an i->j move to an action index
        return self.T*x + y

    def act(self,a):
        #Perform an encoded action, w/ random error
        if random.random() < self.error:
            a = random.randint(0,(self.T**2)-1) #make a random action to do
        #Convert action to move 
        y = a%self.T
        x = (a-y)/self.T

        #Do the actual movement
        ret = self.move(x,y) 
        return ret #Return the results of the move

    def make_state(self):
        #Construct the environmental state

        state = '' #Initial state is empty

        #state = state + str(self.stacks) #Return the whole state

        #Grab specific stack information
        for i in range(len(self.stacks)):
            if len(self.stacks[i]) > 0: #As long as there is something in the stack, calculate state
                state = state + str(self.stacks[i][0:2]) #Grab the top two disks on a stack
                state = state + str(len(self.stacks[i])) #grab the length of the stack
            else:
                state = state + "[]" #If there's not anything on the stack, just add an empty
        #state = state + str(self.act_p) #Add the most recent action to the state

        #Return the constructed string
        return state

###
#
# Experiment Block
#
###

#Experiment variables
ctr_total = 0 #Total counter sum
states_total = 0 #Total states observed
num_T = 20 #Number of trials

num_E = 10 #Number of epochs per trial
e_Exp = 1 #Number of exploration epochs

Towers = 4 #Number of towers in the test
Rings = 5 #Number of disks in the test

E_rate = 0.05 #Error induction rate

s_gi = -1 #Initial goal state

S_lim = 100000 #Max number of simulation cycles per trial

#For each trial
for T in range(num_T):

    Brain = pDIJ_type2.pDIJ_type2(120,Towers**2,0.5,50,55) #Make a new agent

    print(T,"--------------") #Display the trial number

    e = 0 #Reset epoch number

    #For each epoch
    while e < num_E:

        #Make a new puzzle
        puzzle = TOH(Rings,Towers,E_rate)
        s_in = puzzle.make_state() #Get the initial state
        ctr = 0 #Set step counter to zero

        #Until the goal is reached or too many cycles have run
        while len(puzzle.stacks[-1]) != puzzle.N and ctr < S_lim:

            #Grab the state
            state_i = puzzle.make_state()
            Brain.add_state(state_i) #Make sure the agent knows it

            #If in one of the exploration phases
            if e < e_Exp:
                a = random.randint(0,(puzzle.T**2)-1) #Pick a random action

            #Otherwise
            else:
                s_i = Brain.E2S[state_i] #Grab the state
                acts,path = Brain.find_path(s_i,s_g) #Try to make a solution
                if acts != -1: #If a solution was found
                    a = int(acts[0]) #pick the first action from it
                else:
                    a = random.randint(0,(puzzle.T**2)-1) #Otherwise, try a random action

            puzzle.act(a) #Take the action chosen

            state_f = puzzle.make_state() #Get the final state
            Brain.add_state(state_f) #Make sure the agent knows the state

            Brain.update_native(state_i,state_f,a) #Make an update for the observed occasion

            if e >= e_Exp: #If out of the exploration phase
                #If the state is the goal
                if Brain.E2S[state_f] == s_g and len(puzzle.stacks[-1]) != puzzle.N:
                    if s_g == s_gi: #if equal to the prior state
                        s_g = Brain.E2S[s_in] #set new goal to the current state for the reset
                    else:
                        s_g = s_gi #Set goal to the prior one

            ctr+=1 #Increase the step counter

        #On the first epoch
        if e == 0 and ctr != S_lim:
            s_g = Brain.E2S[puzzle.make_state()] #set the prior goal to the state
            s_gi = s_g #update the initial goal

        print(e,ctr,len(Brain.E2S)) #Display the epoch data

        #Increase the epoch counter if the total counter hasn't exceeded the limit
        if ctr != S_lim:
            e += 1






