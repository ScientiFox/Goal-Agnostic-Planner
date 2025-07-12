###
# GAP simulation test, joint TAXI/MAZE problem
#
#  GAP algorithm learning to solve the TAXI problem in a
#  maze context. Mazes are generated at random using self-
#  avoiding polygons, and testing ranges from a small set of
#  disconnected obstacle blocks in a field, to standard
#  right-hand-rule mazes, to ill-conditioned mazes with 
#  loops and cycles.
#
#  Note that training is not designed to learn to navigate in
#  any specific maze, but relativistic local navigation in
#  an arbitrary one.
#
#  Also note that the agent much engage in hierarchical
#  learning, to locate, pick up, and drop off 'passengers'
#  with discreet and active operations, not just arrive
#  at a destination
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

###
# SAP segment
#  for generating random training mazes
###

def get_4_connectivity(G):
    #Function to return the NESW connectivity of cells in a map
    nn = np.shape(G) #Shape of the cells
    conn = np.zeros(nn) #zeroes for connectivity count

    #Summing directions:
    conn[1:,:] = conn[1:,:] + G[:-1,:] #right
    conn[:-1,:] = conn[:-1,:] + G[1:,:] #left
    conn[:,1:] = conn[:,1:] + G[:,:-1] #down
    conn[:,:-1] = conn[:,:-1] + G[:,1:] #up

    #return summed array
    return conn


def get_8_connectivity(G):
    #function to get connectivity in 8 cardinal directions
    nn = np.shape(G)
    conn = np.zeros(nn)

    #sum up NE, NW, SE, and SW directions
    conn[1:,1:] = conn[1:,1:] + G[:-1,:-1]
    conn[:-1,1:] = conn[:-1,1:] + G[1:,:-1]
    conn[:-1,:-1] = conn[:-1,:-1] + G[1:,1:]
    conn[1:,:-1] = conn[1:,:-1] + G[:-1,1:]

    #sum up NESW directions
    conn[1:,:] = conn[1:,:] + G[:-1,:]
    conn[:-1,:] = conn[:-1,:] + G[1:,:]
    conn[:,1:] = conn[:,1:] + G[:,:-1]
    conn[:,:-1] = conn[:,:-1] + G[:,1:]

    #return summed array
    return conn

def local_4_connectivity(k,Pg):
    #Function to get the 4-connectivity of a specfic cell

    #grab the nearby cells
    locs = [(k[0]-1,k[1]),(k[0],k[1]-1),(k[0],k[1]+1),(k[0]+1,k[1])]

    #neighbor count to 0
    neigh = 0
    for a in locs: #for each adjacent cell
        if (a[0]>=0 and a[1]>=0): # if not negative coordinates
            try:
                neigh = neigh + 1*(Pg[a]>0) #add if actually on the map
            except:
                pass #otherwise nothing

    #return the sum of real, counted neighbors
    return neigh

def local_8_connectivity(k,Pg):
    #function to get the 8-connectivity of a specific cell

    N = Pg[k[0]-1:k[0]+2,k[1]-1:k[1]+2] #grab the cells in the map around the current location
    N[1,1] = 0 #set the at-location to 0

    #return the local sum
    return np.sum(N)

def local_25_connectivity(k,Pg):
    #function to get the local 25-connectivity of a cell
    N = Pg[k[0]-2:k[0]+3,k[1]-2:k[1]+3] #grab local region
    N[2,2] = 0 #set center (current position) to 0
    return np.sum(N) #return sum

def snake_check(N):
    #Function to check the local closure of a set of cells

    #Coordinates within the 3x3 grid of a neighborhood
    L = [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]
    s = [0,1,2,4,7,6,5,3]   # indices of coordinates in list by clockwise from top left
                            #       0 1 2
                            #       7 * 3
                            #       6 5 4 hence 'snake' check
    cnt = 0 #counter
    for a in range(len(s)): #looping over snake order
        i = N[L[s[a]]] #grab the value at the next coord to check
        i2 = N[L[s[(a+1)%len(s)]]] #grab the next one
        if i != i2: #if not the same,
            cnt+=1 #count up discontinuities
    return cnt #return number of discontinuities

def get_neighbours(k,Pg):
    #function to get candidate neighbors list around a point
    locs = [-1,(k[0],k[1]-1),(k[0]-1,k[1]),(k[0],k[1]+1),(k[0]+1,k[1])] #make list of locations (-1 for 1 start indexing)
    cands = [1]*(Pg[locs[1]] != 0) + [4]*(Pg[locs[4]] != 0) + [2]*(Pg[locs[2]] != 0) + [3]*(Pg[locs[3]] != 0) #neighbor indexing list
    return cands #return list

def choose_from(Pis):
    # choose from a set of weighted possibilities
    Pt = sum(Pis) #Get the sum of weights
    Pi = [(1.0*a)/Pt for a in Pis] #calculate normalized weights
    cPi = [sum(Pi[:a+1]) for a in range(len(Pi))] #get cumulative sum
    r = random.random() #random number
    i = 1 #index
    while (r > cPi[i]): #loop until finding weight over cumumative sum
        i+=1 #increment index
    return r,cPi,i #return random selection, threshold value and index

def custom_resize(Pg,f):
    #integer block resize of an array by a facror f

    #getshape of initial array
    y,x = np.shape(Pg)[:2]
    yn = f*y #output size scaled by f
    xn = f*x
    if len(np.shape(Pg)) == 2: #if two axes
        imout = np.zeros((yn,xn)) #2 axis output
    else:
        imout = np.zeros((yn,xn,3)) #otherwise 3 axis (ignore additional axes)

    #looping over x and y
    for i in range(y):
        I = f*i #scaled resize index
        for j in range(x):
            J = f*j #scaled resize index two
            try:
                imout[I:I+f,J:J+f] = Pg[i,j] #set fxf sized block to i,j value
            except:
                imout[I:I+f,J:J+f,:] = Pg[i,j,:] #set fxfx? block to i,j value

    #return resized array
    return imout

def get_empty_neighbours(k,Pg):
    # Function to grab the unfilled neighbors

    #1-indexed list for weights
    Pis = [0,0,0,0,0]

    #locations (also 1-indexed) and candidate neighbors
    locs = [-1,(k[0]-1,k[1]),(k[0],k[1]-1),(k[0],k[1]+1),(k[0]+1,k[1])]
    cands = [1]*(1*(Pg[locs[1]] == 0)) + [2]*(1*(Pg[locs[2]] == 0)) + [3]*(1*(Pg[locs[3]] == 0)) + [4]*(1*(Pg[locs[4]] == 0))

    minV = 100000000000 #minimum value (huge for initial comps)
    for a in cands: #for each candidate,
        aV = local_8_connectivity(locs[a],Pg) #check the 8-continuity around it

        if aV < 4: #if less than 4 connections
            Pis[a] = 1.0 #weight is 1.0

    #if no viable weights
    if Pis == [0,0,0,0,0]:
        cands = [] #no candidates!
    return cands,Pis #return candidates and weights

def make_polygon(n,A_lim,step_limit,edge_limit,save):
    #function to make a polygon with parameters
    # A_lim : area limit
    # step_limit : max number of steps
    # edge_limit : maximum number of edges

    # list of cells in polygon, and arrays of the perimeter and added cells
    P = []
    polygon_grid = np.zeros((n,n))
    perimeter_grid = np.zeros((n,n))-1

    #set initial center seed
    polygon_grid[int(n/2),int(n/2)] = 1
    perimeter_grid[int(n/2),int(n/2)] = 0
    P = P + [(int(n/2),int(n/2))]

    #perimeter length and area variables
    P_l = 1
    A = 1

    #sites to check
    sites = [(int(n/2),int(n/2))]

    #state, count of edges, and preceeding area measure
    state = 1
    edgecnt = 0
    A_p = A

    #While area, number of edges, and steps all within limits
    while A < A_lim and edgecnt < edge_limit and step_limit > 0:

        step_limit -= 1 #tick down a step
        if (A%10 == 0 and A > 0): #periodic outputs and saves as we progress
            if A_p != A: #if a new cells added since last time
                #print A,P_l #optional print
                A_p = A #mark new prior area at save
                if save == 1: #if saving the polygons
                    imout = custom_resize(polygon_grid + 2*(perimeter_grid >= 0),10) #upscaled polygon
                    cv2.imwrite("SAP-"+str(A)+".png",imout*80) #write output image

        #Generate a random index of a cell on the perimeter
        rP = random.randint(0,P_l)

        i = 0 #index for loop over perimeter
        j = -1 #selection index
        while (i < rP): #while less than the selected index
            if (P[j] != -1): #if perimeter cell is not empty
                i+=1 #increment counter
            if i < rP: #if less than selection
                j+=1 #increment selection index
        k = P[j] #set k location to the polygon cell on perimeter

        try:
            c = -1 #set c flag
            cands,Pis = get_empty_neighbours(k,polygon_grid) #get local empty neighbors
            if cands != []: #if some cands
                r,cPi,I = choose_from(Pis) #pick one
                locs = [-1,(k[0]-1,k[1]),(k[0],k[1]-1),(k[0],k[1]+1),(k[0]+1,k[1])] #get locations
                k_p = locs[I] # grab new location
            else: #otherwise
                c = -2 #set flag
        except: #if failed
            c = -1 #reset flag
            edgecnt+=1 #increase edge count

        try:
            if c != -2: #if location not found
                N = polygon_grid[k_p[0]-1:k_p[0]+2,k_p[1]-1:k_p[1]+2] #grab region
                c = snake_check(N) #get the snake check in that area
        except:
            c = -1 #if failed, set c flag
            edgecnt+=1  #increase edge count

        #if the snake check set a count of 2
        if (c == 2):
            edgecnt = 0 #reset edge count
            A += 1 #increase area
            if polygon_grid[k_p] != 1: #if the polygon cell is not filled
                sites = sites + [k_p] #add new cell to site list
            P = P + [k_p] #add kp to the polygon
            P_l = P_l + 1 #increase perimeter count
            perimeter_grid[k_p] = len(P)-1 #update perimeter grid with index
            polygon_grid[k_p] = 1 #put active cell in polygon grid

            #grab locations on new cell
            locs = [-1,(k_p[0]-1,k_p[1]),(k_p[0],k_p[1]-1),(k_p[0],k_p[1]+1),(k_p[0]+1,k_p[1])]

            for a in [1,2,3,4]: #for each 1-indexed neighbor
                c_n = local_4_connectivity(locs[a],polygon_grid) #get 4-connectivity
                if c_n == 4: #if all 4 filled
                    if perimeter_grid[locs[a]] != -1: #if not in perimeter
                        P[int(perimeter_grid[locs[a]])] = -1 #remove from perimeter list
                        perimeter_grid[locs[a]] = -1 #remove from perimeter grid
                        P_l = P_l - 1 #decrease perimeter count

    #return the generated polygon, its perimeter, cell list and sites list
    return polygon_grid,perimeter_grid,P,sites

def on_grid(W,p):
    #Wrapper to check if a cell is on a grid of width W
    if (0<=p[0])*(p[0]<W)*(0<=p[1])*(p[1]<W):
        return 1
    else:
        return 0


def data_organize(run_data,index):
    # function to sort data from trials

    num = len(run_data) #number of data trials
    length = len(run_data[0]) #size of runs in a trial

    S = ['']*length #Strings for each run

    for a in range(num): #looping over each trial
        for b in range(length): #looping over single run data
            S[b] = S[b] + str(run_data[a][b][index]) + ',' #make a csv string

    #remove all trailing commas
    for a in range(len(S)):
        S[a] = S[a][:-1]

    #return list of strings
    return S


class sim:
    #Class for a TAXI/MAZE simulation world

    def __init__(self,_W,_E):
        #start up with width and error rate specified
        self.W = _W
        self.E = _E

        #indexed lists of directional moves by index 0-3
        self.dirs = [np.array([[(1-d)*(d%2==0),(2-d)*(d%2==1)]]) for d in range(4)]

        #make a grid for world layout and points of interest sites
        self.grid = np.zeros((self.W,self.W))
        self.POIs = np.zeros((self.W,self.W))-1

        #flags for passenger state and location state
        self.passenger = -1
        self.location = -1

        #internal states
        self.state = -1 #current state
        self.act_p = -1 #prior action
        self.sites = [] #list of sites
        self.POIl = [] #list of points of interest
        self.state_p = "" #prior state string
        self.state_p_full = "" #full non encoded prior state
        self.act_p = 0 #Prior action
        
    def init_canonical(self,n_sites,n_POIs):
        # initialize an actual experiment

        pos = (random.randint(0,self.W-1),random.randint(0,self.W-1)) #init position
        dr = [(-1,0),(0,-1),(1,0),(0,1)] #position changes

        #Make Maze
        Pg,Prg,Pl,St = make_polygon(self.W,n_sites,25000,50,0)

        self.grid = 1 - Pg #invert Pg for grid
        site_list = St #sites list

        self.POI_list = [] #list of points of interest

        #Make POIs
        for a in range(n_POIs):
            rl = random.randint(0,len(site_list)-1) #random index
            self.POI_list = self.POI_list + [site_list[rl]] #grab a site and add to list
            site_list = site_list[:rl] + site_list[rl+1:] #remove from site list

            #add pois as index to array
            self.POIs[int(self.POI_list[-1][0]),int(self.POI_list[-1][1])] = len(self.POI_list)-1
            self.POIl = self.POIl + [len(self.POI_list)-1] #add index to list

        #Make Destination
        rl = random.randint(0,len(site_list)-1) #random index
        self.D = site_list[rl] #set destination
        self.grid[int(self.D[0]),int(self.D[1])] #mark on grid

        self.sites = site_list #load new site list into object

        r = random.randint(0,len(self.sites)-1) #random site
        self.set_location(self.sites[r]) #set start location

        #return when done
        return 1

    def move(self,d):
        #Method to move agent on grid

        m = self.dirs[d] #grab movement vector
        location_p = self.location + m #hypothetical new location

        if on_grid(self.W,(location_p[0,0],location_p[0,1])): #check if on the grid
            if self.grid[int(location_p[0,0]),int(location_p[0,1])] != 1: #if not a wall,
                self.location = location_p  #update location
                return 1 #return success
            else: #otherwise
                return -1 #return failure and don't move into a wall
        else: #if not on grid
            return -1 #don't move off grid

    def pickup(self):
        #agent action to pick up passenger

        l = (self.location[0,0],self.location[0,1]) #grab location
        if self.POIs[int(l[0]),int(l[1])] != -1 and self.passenger == -1: #if passenger at, and don't have one already
            self.passenger = self.POIs[int(l[0]),int(l[1])] #get passenger
            self.POIs[int(l[0]),int(l[1])] = -1 #clear passenger from POI
            return 1 #return success
        else: #otherwise
            return -1 #return failure

    def dropoff(self):
        #method to drop off passenger

        l = (self.location[0,0],self.location[0,1]) #get location
        if l == self.D and self.passenger != -1: #if location is destination and you have passenger
            self.POIl.remove(self.passenger) #remove passenger from list
            self.passenger = -1 #remove passenger from agent
            return 1 #return success
        elif self.POIs[int(l[0]),int(l[1])] != -1: #if another passenger's location
            return -1 #return failure
        elif l != self.D: #id not the passenger's destination
            return -1 #return failure

    def act(self,_act):
        #method to take an agent action

        self.act_p = _act #set prior action
        if random.random() < self.E: #if under error addition threshold
            ret = random.randint(0,3) #random action
        else: #otherwise
            if self.act_p in [0,1,2,3]: #if a movement
                ret = self.move(self.act_p) #do the move
            elif self.act_p == 4: #if a pickup
                ret = self.pickup() #try pickup
            elif self.act_p == 5: #if a dropoff
                ret = self.dropoff() #do dropoff
            else: #otherwise
                self.act_p = -1 #mark invalid action
                ret = -1 
            if ret != -1: #if a valid action 
                self.act_p = _act #set prior
            else: #otherwise
                self.act_p = -1 #invalid action
        return ret #return return code

    def set_location(self,p):
        #wrapper to set a location directly
        if (p[0] < self.W) and (p[1] < self.W):
            self.location = np.array([[p[0],p[1]]])
            return 1
        else:
            return -1

    def passAt(self):
        #wrapper to check if a passenger is present
        if self.POIs[int(self.location[0,0]),int(self.location[0,1])] != -1:
            return 1
        else:
            return 0

    def atD(self):
        #wrapper to check if at destination
        if (self.location[0,0],self.location[0,1]) == self.D:
            return 1
        else:
            return 0

    def scan_obstacles(self):
        #Method to get local obstacles - several different abstractions

        v = [] #list of obstacle presence
        for a in self.dirs: #over each direction
            sweep = self.location + a #look in that direction
            if on_grid(self.W,(sweep[0][0],sweep[0][1])): #if on the grid
                v = v + [self.grid[sweep[0][0],sweep[0][1]]] #add the cell's state (occupied or open)
            else: #otherwise
                v = v + [1] #Mark off the grid as blocked
        return v #return list

    def state_make(self):
        #method to construct a state string - many options

        state = '' #initial empty string

        ### One option of state string, variable including and of the following components:
        state = state + str(int(self.location[0,0])) + ":"
        state = state + str(int(self.location[0,1])) + ":"
        state = state + str(1*(self.passenger!=-1)) + ":"
        state = state + str(len(self.POIl)) + ":"
        state = state + str(self.passAt()) + ":"
        state = state + str(self.atD())
        ###

##        #another set of state options:
##        Lx = int(self.location[0,0]) #XY location
##        Ly = int(self.location[0,1])
##        B = self.grid[Lx-1:Lx+2,Ly-1:Ly+2] #local area, 3x3
##        #B = self.grid[Lx-2:Lx+3,Ly-2:Ly+3] #local area 5x5
##        k = np.shape(B)[0]*np.shape(B)[1] #flatten length of local area
##        B = np.reshape(B,(1,k)) #flattened area
##
##        for a in [1,3,5,7]: #grabbing a subsample of the area and adding to string
##            state = state + str(int(B[0,a]))+":"
##
##        state = state + str(B) + ":" #separator
##
##        B2 = self.grid[Lx-2:Lx+3,Ly-2:Ly+3] #local area in 5x5 grid
##        state = state + str(np.sum(B2)) + ":" #sum of local obstacles and separator
##
##        #state = state + str(self.act_p) + ":" #optional prior action
##
##        #Temporally linked state (like Murin ML algorithm, for instance)
##        state_o = state #non-augmented state
##        state = state + self.state_p #Add prior state to full state
##        self.state_p = state_o #put non augmented state into prior state slot
##
##        #state = state + ":"
##
##        state = state + str(1*(self.passenger!=-1)) + ":" #whether currently has a passenger
##
##        #if there are passengers left
##        if len(self.POIl) > 0:
##
##            #generic direction towards next destination - four effective models
##            P_vec = [self.POI_list[self.POIl[0]][0]-self.location[0,0],self.POI_list[self.POIl[0]][1]-self.location[0,1]]
##            #P_vec = round(math.atan(P_vec[0]/P_vec[1]),4) #option two
##            P_vec = [(a<0)*(-1)+(a>0)*(1) for a in P_vec] #binarization option
##            #P_vec = [abs(a) for a in P_vec] #magnitude option
##
##            #state = state + str(P_vec) + ":" #add direction vector
##
##        else:
##            state =  state + "None" + ":" #otherwise no passenger state
##
##        #state = state + str(self.POIl) + ":" #Add passenger list to state
##        state = state + str(self.passAt()) + ":" #add passenger at to state
##        state = state + str(self.atD()) #add at destination to state

        #Finally, return constructed state
        return state

###
#
# Experiment block
#
###

Tests = 25 #Number of tests to run
N_exp = 2 #exploration phases

N = 30 + N_exp #Total experiments plus explorations 

#World variables
W = 15 #Width
P = 0.7 #maze density
A = 2 #Number of passengers

#Menu of error rates to experiment with
E_list = [0.01,0.05,0.1,0.15,0.2,0.25]

for E in E_list: #For each error to test

    print(E,"----------------------") #display separator

    run_data = [] #Data for this trial

    Data_fin = [(0,0,0)]*N #holder for output data
    avg_brain=np.zeros((2000,2000)) #brain to average over all tests

    for T in range(Tests): #Loop over the number of tests

        print(str(T)+",", end = '') #Print test number

        n = 0  #Experiment number

        #Build world for this test
        world = sim(W,E)
        world.init_canonical(int(P*W*W),A)
        world_pristine = copy.deepcopy(world)

        #Make an agent brain
        Brain = pDIJ_type2.pDIJ_type2(40,6,0.01,20,22)
        acts_tried = [0]*60 #actions tried tabu list

        #Write image of this maze
        cv2.imwrite("maze.png",(1-world.grid)*255.0)

        ctr = 0 #step counter
        s_g = -1 #goal state flag
        non_guess = 0 #count of times the agent made a planned, non-guess action
        total_acts = 0 #total number of actions taken
        p_ct = 0 #random exploration count

        Tabu = {} #Tabu exploration lookup
        T_num = {} #tabu lookup counts
        Tn = 0 #Tabu index counter
        state_p = 0 #Prior state

        #Looping over number of trials
        while n < N:

            ctr+=1 #increment step counter
            total_acts+=1 #increment number of actions

            state_i = world.state_make() #Make the state

            acts = -1 #actions flag
            acts = [] #actions list

            #If the goal state is visible and so is the current state, and out of explore phase
            if (s_g in Brain.E2S) and (state_i in Brain.E2S) and (n >= N_exp):
                acts,path = Brain.find_path(Brain.E2S[state_i],Brain.E2S[s_g]) #get a path

            Brain.add_state(state_i) #add current state
            s_i =  Brain.E2S[state_i] #grab index state

            #if no action choice found
            if acts == -1 or acts == []:
                if s_i >= len(acts_tried): #if no tabu list for current state, make list longer to account
                    acts_tried = acts_tried + [0]*(s_i-len(acts_tried)+1)

                #cycling over 20 sets of all actions
                k=20
                if acts_tried[s_i] == 6*k-1: #if uniformly tried actions in this state
                    a = random.randint(0,5) #just full random survey
                else: #if still uniformly searching
                    a = (acts_tried[s_i]%6) #get next one to try evenly
                    acts_tried[s_i] = acts_tried[s_i] + 1 #increment counts
                p_ct+=1 #increase explore count

            else: #if not doing tabu search on this state
                non_guess+=1 #increment counter for non guess actions
                a = int(acts[0]) #get the action

                # Alternative probabilistic action selection
                #Pa = Brain.AF[1,path[0],path[1]]
                #r = random.random()
                #if r > Pa and Pa < 0.5:
                #    a = random.randint(0,5)

            #Actually do the action
            world.act(a)

            #make the state
            state_f = world.state_make()

            #Update the brain's learning
            Brain.update_native(state_i,state_f,a)

            #Grab index states
            si = Brain.E2S[state_i]
            sf = Brain.E2S[state_f]

            # Optional in progress output
            #if (n > 0):
            #    print(n,ctr,a,Brain.E2S[state_i],Brain.E2S[state_f],Brain.INC[:,si,sf])

            #if no passengers
            if world.POIl == []:
                s_g = state_f #Goal state reached
                world = copy.deepcopy(world_pristine) #Make a new initial world copy

                #Update average brain for this trial
                avg_brain[:np.shape(Brain.AF)[1],:np.shape(Brain.AF)[2]] = avg_brain[:np.shape(Brain.AF)[1],:np.shape(Brain.AF)[2]] + (Brain.AF[1,:,:])/(1.0*Tests)

                #Make up trial print data
                Dd = [ctr,round(non_guess/(1.0*ctr),2),Brain.S]

                #Format and print trial data
                D = 'Done: ' 
                for a in Dd:
                    D = D + str(a) + ","
                print(D[:-1])

                #Add trial data to experiment data set
                Data_fin[n] = [Data_fin[n][0] + ctr/(1.0*Tests),Data_fin[n][1] + round(non_guess/(1.0*ctr),2)/(1.0*Tests),Data_fin[n][2] + Brain.S/(1.0*Tests)]

                #Reset tracker variables
                non_guess = 0
                n += 1
                ctr = 0

    #After experiment, print final data
    print()
    print("Fin Data ----------------")

    #Open output files- data and brain
    f = open("GAP TAXI W="+str(W)+" P="+str(P)+" A="+str(A)+" E="+str(int(E*100)),'w+')
    cv2.imwrite("data_TAXI_brain_"+str(E)+".png",avg_brain*255.0)

    #Write out data to file, and print it
    for a in range(len(Data_fin)):
        print(a,Data_fin[a][0],Data_fin[a][1])
        f.write(str(a) + "," + str(round(Data_fin[a][0],2)) + "," + str(round(Data_fin[a][1],2)) + "\n")

    #Close the file before something happens to it
    f.close()
