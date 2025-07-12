###
#
# Binary Addition toy problem
#
#  Example of the GAP algorithm learning to solve binary addition
#
###'''

#Standards
import math,time,random

#For linear algebra
import numpy as np

#For file handling
import copy,pickle

#Import GAP algorithm agent
import pDIJ_type2 

def cvt_to_bin(n):
    #Lightweight conversion of interger to binary list
    b = []
    i = math.floor(math.log(n,2))
    while i >= 0:
        g = (n >= 2**i)
        b.append(1*g)
        n = n - (2**i)*(g)
        i-=1
    return b

def cvt_to_dec(b):
    #Lightweight conversion from binary list to integer
    i = len(b)-1
    n = 0
    while (i >= 0):
        n = n + (2**i)*b[len(b)-i-1]
        i-=1
    return n

def add_bin(a,b):
    #Add two binary lists a and b together
    carry = 0 #Carry digit

    i = max([len(a),len(b)])-1 #Furtraw sumhest digit index

    #Sum and carry lists
    d = [0]*(i+1)
    c = [0]*(i+1)

    #Equal-digit length addend lists
    a = [0]*(i+1-len(a)) + a
    b = [0]*(i+1-len(b)) + b

    #For each digit index
    while (i >= 0):
        s = carry+a[i]+b[i] #Calculate 
        d[i] = s%2 #Grab new digit
        c[i] = carry #Grab prior carry slot
        carry = 1*(s>1) #Get new carry
        i-=1 #Move index
    d = [1]*carry + d #Insert sum into list
    c = [0]*carry + c #Insert carry into list
    return d,c #Return result and carry lists

def get_state(i1,i2,c,d,do,ind):
    #Function to make environmental state variable
    # Commenting lines takes them out of the state

    s1,s2,s3,s4,s5 = ""

    s1 = str(i1) + "," #First addend value at index
    s2 = str(i2) + "," #Second addend value at index
    s3 = str(c) + "," #Carry list
    s4 = str([1*(d[a]==do[a]) for a in range(len(d))])+"," #Whether all digits in the output and sum are the same
    s5 = str(ind)+"," #Current index

    return s1+s2+s3+s4+s5

#Number of epochs per trial and number of trials
E = 20
trials = 100
#err = 0.2 error level, for error inducement experiments

#Run trial sets over numbers of digits
for N in [2,3,4,5,6]:
    
    t_dat = [0]*E #Trial data list

    #For each trial
    for t in range(trials):
        epoch = 0 #Start at 0 epoch

        brain = pDIJ_type2.pDIJ_type2(8*8*N*N,4,0.9,3,5) #Create a new agent
        e_dat = [] #Epoch data list

        #Loop over E many epochs
        while epoch < E:
            epoch+=1 #Increment counter

            #Grab a random pair of addends
            a = cvt_to_bin(random.randint(1,2**N))
            b = cvt_to_bin(random.randint(1,2**N))

            #Set index pointer
            i = N#max([len(a),len(b)])

            #Regularize pad with 0s for overflow
            a = [0]*(i+1-len(a)) + a
            b = [0]*(i+1-len(b)) + b

            #Get sum and carry lists
            d,c = add_bin(a,b)
            do = [0]*len(d)

            #Set of all base viable goal states
            goals = [[0,0,0,N+1],
                     [0,0,1,N+1],
                     [0,1,0,N+1],
                     [0,1,1,N+1],
                     [1,0,0,N+1],
                     [1,0,1,N+1],
                     [1,1,0,N+1],
                     [1,1,1,N+1]]

            #Add goal states to the agent
            gs = [] #list of converted goal states
            for g in goals:
                for i in range(N):
                    sg = get_state(g[0],g[1],g[2],d,d,i) #Make a goal state for each index position
                    brain.add_state(sg) #Ad the state to the agent
                    gs = gs + [sg] #Add the full goal state to the list

            #Trial variables
            stg = 0 #Number of steps to reach the goal
            a_sel = 0 #Selected action
            sf = None #current state (initialized to zero)
            car = 0 #Carry variable state
            ind = i #Insex state

            #Until reaching a goal state
            while not(sf in gs):

                #Grab the digits at the current index
                i1 = a[ind]
                i2 = b[ind]
                si = get_state(i1,i2,car,d,do,ind) #Produce current state
                brain.add_state(si) #Make sure the state is in the agent

                #If not in the random phase
                if epoch > 1:
                    ap = -1 #Initial action plan- initially -1
                    ap_L = 9999 #Initial plan length, initially unreasonably high

                    #For each possible goal
                    for sg in gs:
                        acts,path = brain.find_path_native(si,sg) #Get a solution plan
                        if acts != -1: #and random.random() < err: #If a viable plan is found - latter commented snip is for error inducement
                            if ap_L > len(path): #If the current path is shorter
                                ap_L = len(path) #Set the new plan length to that of the one found
                                ap = acts[0] #Set the action choice to 

                    #If a planned action is found
                    if ap != -1:
                        act = int(ap) #Set it to the integer value for execution
                        a_sel+=1 #Increment the selected action counter
                    else:
                        act = random.randint(0,3) #Otherwise act randomly for exploration
                else:
                    #If in the exploration phase, act randomly (without bothering to do a lookup since no solution could be findable)
                    act = random.randint(0,3)

                #Execute the action picked
                if act == 0:
                    do[ind] = 1-do[ind] #Togle the output digit at the current index
                elif act == 1:
                    car = 1-car #Toggle the carry bit at the current index
                elif act == 2:
                    ind = (ind+1)*(ind < N) + (ind)*(ind == N) #Move the index pointer up
                elif act == 3:
                    ind = (ind-1)*(ind>0) + (ind)*(ind==0) #Move the index pointer down

                #Grab the post-action state
                i1 = a[ind] 
                i2 = b[ind]
                sf = get_state(i1,i2,car,d,do,ind)
                brain.add_state(sf)

                #Update the agent on the si,sf,act occasion observed
                brain.update_native(si,sf,act)

                #Increment the states-to-goal counter
                stg+=1
            e_dat = e_dat + [stg] #Update the epoch data with the stg counter after reaching the goal

            #print(epoch,stg,a_sel) #Optional per-epoch output

        #For each observed epoch
        for dp in range(len(e_dat)):
            t_dat[dp] = t_dat[dp] + e_dat[dp] #Add the epoch data to the trial data

    #At the end of a set of trials, print out the data
    print("Nb = ",N+1,"--------") #Number of digits
    for dp in range(len(t_dat)): #For each trial 
        print(dp,(1.0*t_dat[dp])/trials) #Print the trial number an the average number of steps to the goal












