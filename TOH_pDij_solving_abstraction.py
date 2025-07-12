###
# GAP simulation test, Tower of Hanoi Puzzle
#
#  GAP algorithm learningt o solve the Tower of Hanoi
#  puzzle, across multiple different problem scales, 
#  selected as combinations of numbers of rings and numbers
#  of pegs.
#
#  This iteration explores performance on state abstraction
#  mechanisms
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

    def make_state(self,mode):
        #Modified state method with multiple modes

        state = '' #Initial state is empty

        if mode == 0: #most basic state- just the string of the stacks themselves
            state = state + str(self.stacks)

        elif mode == 1: #First abstraction- 
            for i in range(len(self.stacks)): #looping over stacks
                if len(self.stacks[i]) > 0: #if not an empty stack
                    ###
                    #Note that lower error tolerance is an indication
                    #of compressive abstraction
                    ###
                    state = state + "[" + str(sum(self.stacks[i])) + "]" #Add up sum of rings of stacks
                    state = state + str(self.stacks[i][0]) #and top ring on stack
                else:
                    state = state + "[]" #For empty stacks

        elif mode == 2: #Second abstraction-
            for i in range(len(self.stacks)): #looping over stacks
                if len(self.stacks[i]) > 0: #If not empty stack
                    state = state + "[" + str(len(self.stacks[i])) + "]" #Add up height of stacks
                    state = state + str(self.stacks[i][0]) #And top ring on each stack
                else:
                    state = state + "[]" #For empty stacks

        elif mode == 3: #Third abstraction-
            for i in range(len(self.stacks)): #Looping over stacks
                if len(self.stacks[i]) > 0: #If not empty
                    state = state + "[" + str(len(self.stacks[i])) + "]" #Combine height and sum, but no individual rings
                    state = state + "[" + str(sum(self.stacks[i])) + "]"
                else:
                    state = state + "[]" #For empty stacks

        elif mode == 4: #Fourth abstraction-
            for i in range(len(self.stacks)): #Looping over stacks
                if len(self.stacks[i]) > 0: #If not empty
                    state = state + str(self.stacks[i][0]) #Add in top ring
                    #state = state + "[" + str(sum(self.stacks[i])) + "]" #Optional sum of stack
                    #state = state + "[" + str(len(self.stacks[i])) + "]" #Optional height of stack
                else:
                    state = state + "[]" #For empty stacks

        #Return constructed state
        return state


###
#
# Experiment Block
#
###

num_T = 5 #Number of tests
num_E = 10 #Number of epochs
e_Exp = 1 

#Puzzle type to solve
Towers = 4
Rings = 5

S_lim = 100000 #Ultimate step limit

#Make test assay

E_sample = [0.05*(a) for a in range(9)]
L_sample = [100]

# Alternative test plan
#E_sample = [0.01,0.05,0.1]
#L_sample = [50*(i+1) for i in range(1)]

#Test assay holder
assay = []

#Looping over all combinations
for a in range(len(L_sample)*len(E_sample)*4):

    #Construct test parameters
    L_n = (a - a%(len(E_sample)*4))/(len(E_sample)*4) #Test length index
    ap = a - L_n*(len(E_sample)*4)
    E_n = (ap - a%4)/4 #Which error rate index
    ap = ap - E_n*4 
    state_m = 1 #which state mode to use

    E_a = E_sample[int(E_n)] #Grab error rate
    L_a = L_sample[int(L_n)] #Grab length of run
    test = (state_m,E_a,L_a) #Make a test parameter set
    assay = assay + [test] #Add test to set

#Run simulation

Data_Full = [] #Full output data

for trial in assay: #Looping over all test parameters
    
    state_mode = trial[0] #Grab state mode
    E_rate = trial[1] #grab error
    L = trial[2] #Grab test length

    Data = [[0]*num_E]*num_T #Make data holder
    Data_cum = [(0,0,0,0)]*num_E #Make cumulative data holder

    #Print the trial to run
    print(trial)

    for T in range(num_T): #looping over the number of tests
        print("  ",T,trial) #Print the trial index

        #Make a new brain
        Brain = pDIJ_type2.pDIJ_type2(700,Towers**2,0.01,L,L+int(0.1*L))

        #Set list of trials
        trials = [[a for a in range(Towers**2)]]*Brain.S

        e = 0 #Epoch number
        while e < num_E: #While less than number of epochs

            #Make a new puzzle, get state
            puzzle = TOH(Rings,Towers,E_rate)
            s_in = puzzle.make_state(state_mode)

            ctr = 0 #steps counter

            #Grab init time for tracking
            timer_check = time.time()

            fp_check = 0.0 #Find path time check
            ct_rand = 0 #random action counter
            ct_plnd = 0 #planned action counter

            #While puzzle not solved and less than step limit
            while len(puzzle.stacks[-1]) != puzzle.N and ctr < S_lim:

                #Every 300 steps past 1000, print status update
                if (ctr > 1000) and (ctr%300 == 0):
                    #Print status
                    print("        ",ctr,round(time.time()-timer_check,3),Brain.S,fp_check)
                    if time.time()-timer_check >= 20.0 and (ctr > 1300):
                        ctr = S_lim #Kill loop if >20.0 seconds past last check in and over 1300 steps so far
                    timer_check = time.time() #reset time
                    fp_check = 0.0 #reset path timing check

                #Get state
                state_i = puzzle.make_state(state_mode)
                new_s = Brain.add_state(state_i) #Add state if not in

                #If a new state discovered, add a new trials set
                if new_s:
                    trials = trials + [[a for a in range(Towers**2)]]

                #If in explore phase
                if e < e_Exp:
                    s_i = Brain.E2S[state_i] #Get state index
                    rand = random.randint(0,len(trials[s_i])-1)  #Grab random state index
                    a = trials[s_i][rand] #pull an action 
                    trials[s_i] = trials[s_i][:rand] + trials[s_i][rand+1:] #remove from the tabu trials phase
                    if len(trials[s_i]) == 0: #if trials exhausted
                        trials[s_i] = [a for a in range(Towers**2)] #reset list of them
                else: #If not exploring any more
                    s_i = Brain.E2S[state_i] #get state

                    t3 = time.time() #mark time
                    acts,path = Brain.find_path(s_i,s_g) #Find path
                    t4 = time.time() #mark time

                    if ctr>1000: #if past 1000 steps
                        fp_check = fp_check + (t4-t3) #update find path timer 
                    
                    if acts != -1: #If there's an action to take
                        a = int(acts[0]) #grab it
                        ct_plnd+=1 #increment planned action counter
                    else: #Otherwise
                        rand = random.randint(0,len(trials[s_i])-1) #random trial from trials set
                        a = trials[s_i][rand] #get random action for that set
                        trials[s_i] = trials[s_i][:rand] + trials[s_i][rand+1:] #remove that action from set
                        if len(trials[s_i]) == 0: #if no more tries to do
                            trials[s_i] = [a for a in range(Towers**2)] #reset list
                        ct_rand+=1 #increment random trial counter

                #Take selected action
                puzzle.act(a)

                #Get resultnt state
                state_f = puzzle.make_state(state_mode)

                #Add state to brain if not seen
                new_s = Brain.add_state(state_f)
                if new_s: #if not seen, add a trials set for it
                    trials = trials + [[a for a in range(Towers**2)]]

                #Update the brain's learning
                Brain.update_native(state_i,state_f,a)

                #increment steps counter
                ctr+=1

            #if on the zero epoch and below the step limit before finishing
            if e == 0 and ctr != S_lim:
                s_g = Brain.E2S[puzzle.make_state(state_mode)] #set goal state to final state as encoded now

            #Print out update of data from this run
            print("    ",e,ctr,ct_rand,ct_plnd)

            #If not at the step limit
            if ctr != S_lim:
                Data[T][e] = (ctr,len(Brain.E2S)) #Get run data
                c = Data_cum[e][0] + ctr #add up cumulative step count
                s = Data_cum[e][1] + Brain.S #add up cumulative  state count
                c_r = Data_cum[e][2] + ct_rand #add up cumulative random actions
                c_p = Data_cum[e][3] + ct_plnd #add up cumulative planned actions
                Data_cum[e] = (c,s,c_r,c_p) #Set data
                e += 1 #increment epoch counter

    #Output the data for this experiment
    print("  Data: >>>>>>>>>>>>>>")
    Data_Full = Data_Full + [(trial,num_T,Data_cum)] #Add data from experiment to full data
    for b in range(len(Data_cum)): #For each cumulative sum
        #Convert data frame to averages and print
        print("    ",b,Data_cum[b][0]/(1.0*num_T),Data_cum[b][1]/(1.0*num_T),Data_cum[b][2]/(1.0*num_T),Data_cum[b][3]/(1.0*num_T))

#Note that experiments are done
print("Assay Complete")
print("Data Available in Data_Full var")

#Build output strinfs
out_strs = [""]*(num_E+1) #Over all the errors tested
for a in Data_Full: #looping over all data
    out_strs[-1] = out_strs[-1] + str(a[0]) + ", , , , " #Header
    for b in range(len(a[2])): #for each entry in data frame
        #Add CSV of reported data to string
        out_strs[b] =  out_strs[b] + str(a[2][b][0]/a[1]) + ", " + str(a[2][b][1]/a[1]) + ", " + str(a[2][b][2]/a[1]) + ", " + str(a[2][b][3]/a[1]) + ", "

#Open a save file
f = open("TOH_data_file.txt","w+")
for a in out_strs:
    f.write(a+"\n") #write all CSV output data to file
f.close() #Close file before something happens to it





