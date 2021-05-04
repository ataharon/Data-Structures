import pytest
import math
import random
import heapq

# Positive and negative infinity
PINF =  float('inf')
NINF = -float('inf')

# returns the distance between two points
#maybe modify to compare diff dimensions?
def distance(p1, p2):
    
    #answer should be in greater number of dimensions
    dimensions = max(len(p1), len(p2))
    
    #fill in the lower dimensional point with 0s
    if len(p1) < dimensions:
        for i in range(dimensions-len(p1)): p1 += (0,)
    
    else:
        for i in range(dimensions-len(p2)): p2 += (0,)
    
    
    #calculate Euclidean distance
    sum = 0
    for i in range(dimensions):
        di = p1[i] - p2[i]
        sum += di**2
    
    return math.sqrt(sum)  

#returns the max distance between the pivot and a list of child points
def maxDistance(pivot, pairs):

    radius = 0

    #for each point, if distance from pivot is greater than max, make it max
    for p in pairs:
        
        #the "point" is the key of the pair
        dist = distance(p[0],pivot[0]) 
        if dist > radius: radius = dist
        
    return radius

#returns the dimension of greatest spread
def findDGS(pairs):
    DGS = 0
    
    #the number of dimensions is the length of any key
    numDimensions = len(pairs[0][0])
    
    #in each dimension, find the least and greatest value
    #keep track of maxs and mins in a list the length of numDimensions
    maxs = [NINF] * numDimensions
    mins = [PINF] * numDimensions
    
    #for each key, see if its value in any dimension is the max or min
    for pair in pairs:
        key = pair[0]
        for i in range(numDimensions):
            
            #if value of a dimension is greater than max, make it the max
            if key[i] > maxs[i]: maxs[i] = key[i]
            
            #do the same for mins
            if key[i] < mins[i]: mins[i] = key[i]
            
    #now the maxs and mins should be full of the max and min values
    #at each dimension
    #compare the difference between max and min at each dimension
    #to find the DGS
            
    maxSpread = 0
    
    #for each dimension, if the spread is greater than the max spread,
    #make it the DGS
    for i in range(numDimensions):
        if maxs[i] - mins[i] > maxSpread:
            maxSpread = maxs[i] - mins[i]
            DGS = i    
    
    return DGS

#returns the median point based on the DGS
#(consider changing to median of 5 or 7)
def medianOfThree(points, DGS):
    
    #choose 3 random points in the list
    a = random.choice(points)
    b = random.choice(points)
    c = random.choice(points)
    
    #isolate values at DGS
    aDGS = a[0][DGS]
    bDGS = b[0][DGS]
    cDGS = c[0][DGS]
    
    #conditions when a is median
    if (aDGS <= bDGS and aDGS >= cDGS) \
       or (aDGS >= bDGS and aDGS <= cDGS):
        median = a
       
    #do the same tests for b
    elif (bDGS <= aDGS and bDGS >= cDGS) \
       or (bDGS >= aDGS and bDGS <= cDGS):
        median = b
    
    #if not then it must be c   
    else:
        median = c     
        
    return median


class Node(object):
    
    #a Node stores one pair and has a left and right child
    def __init__(self, pair, leftChild=None, rightChild=None, radius=0):
        self.key = pair[0]
        self.data = pair[1]
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.radius = radius
        

class BallTree(object):

    #builds a ball tree given a list of (key, data) pairs
    def __init__(self, pairs):
        
        #self.__numPoints = len(pairs)
        
        #build a ball tree with the list of all pairs and store it as the root
        self.__root = self.__build(pairs)
        
        
        
    #builds a ball tree and returns the root node 
    def __build(self, pairs):
        
        #base case: one pair
        if pairs and len(pairs) == 1:
            
            #create a leaf node
            n = Node(pairs[0])
        
        #more than one pair:
        #elif pairs and len(pairs) > 1:
        else:
            #find the dimension of greatest spread (DGS)
            DGS = findDGS(pairs)
            print("pairs:",pairs)
            print("DGS:", DGS)
                    
            #choose a central point considering the DGS
            pivot = medianOfThree(pairs, DGS)
            print("pivot:",pivot)
         
            #separate the points into left and right
            leftPoints = []
            rightPoints = []
            
            #for each point, add to correct pile
            for pair in pairs:
                
                #leave out the pivot
                if pair != pivot:
                    
                    #if the value at the DGS is <= pivot's, add to left
                    if pair[0][DGS] <= pivot[0][DGS]: leftPoints += [pair]
                
                    #otherwise, add to right
                    else: rightPoints += [pair]
                
            print("left points:", leftPoints)
            print("right points:", rightPoints)
                
            #if there are no points in left child, set it to None
            if len(leftPoints) == 0: leftChild = None
                
            #otherwise, build the child
            else: leftChild = self.__build(leftPoints)
            
            #do the same for the right child
            if len(rightPoints) == 0: rightChild = None
            else: rightChild = self.__build(rightPoints)
            
            #find the radius = 
            #the distance from the pivot to the furthest child point
            maxLeft = maxDistance(pivot, leftPoints)
            maxRight = maxDistance(pivot, rightPoints)
            radius = max(maxLeft, maxRight)
                
            #create a Node with 2 children
            n = Node(pivot, leftChild, rightChild, radius)
        
        print("Node:", n.key, ",", n.data)
        return n
    
    
    #finds the data at this exact key
    #if key does not exist, returns None
    def findExact(self, key, n='start'):
        
        #start from the root
        if n=='start': n = self.__root
        
        #base case: reached the end
        if not n: return None
        
        #compute distance from pivot point to search point
        dist = distance(n.key, key)
        
        #see if the point is within the radius of this node
        #if not, it cannot be found
        if dist > n.radius: return None
        
        #otherwise, it may be there
        #see if it's equal to pivot
        if key == n.key: return n.data
        
        #if not, recurse into children
        else: 
            
            #first check left child
            ans = self.findExact(key, n.leftChild)
            if ans: return ans
            
            #if not found in left, search right
            return self.findExact(key, n.rightChild)

    
    
    #finds the k nearest neighbors to a specified point
    #returns a list of the neighbors' (key, data) pairs
    #if fewer than k points exist, return a list of all pairs
    def kNearestNeighbor(self, key, k, n='start', heap=[(NINF,(0,0),0)]):
        
        #start with the root
        if n == 'start': n = self.__root
        
        #initialize max heap as a list of 5 infinities
        #keep heap values negative to make it a max heap (default is min)
        #heap = [(NINF,(0,0),0)]
        #ans = []
        
        #base case: reached end
        if not n: return heap
        
        #calculate (and negate) distance from node's key to search key
        dist = -distance(n.key,key)
        
        #if the answer can't be within this circle, don't search any further
        #the closest possible point would be 
        #the distance to the pivot - the distance to the radius
        #if that value is greater than the current max (less since negative), 
        #it can't be in ans
        if dist + n.radius < heap[0][0]: return heap
        
        #if it can be in the circle, see if the node's key makes it
        else: 
            
            #if the heap isn't full yet, definitely add
            if len(heap) < k: heapq.heappush(heap,(dist,n.key,n.data))
            
            #if the heap is full,
            #if the distance is less than the max so far (greater if negative)
            #add it to the heap

            elif dist > heap[0][0]: 
                heapq.heappush(heap,(dist,n.key,n.data))
                
                #remove the max
                heapq.heappop(heap)
                #ans = [(i[1][1],i[1][2]) for i in heap]  
                
        
            #recurse into children
            #decide whether to go into child or not*
            self.kNearestNeighbor(key, k, n.leftChild, heap)
            self.kNearestNeighbor(key, k, n.rightChild, heap)
            
        return [(i[1],i[2]) for i in heap]
            
        
    
    #displays the nodes in the tree
    def display(self, n='start', kind="ROOT:  ", indent=""):

        if n=='start': n = self.__root
        print("\n" + indent + kind, end="")
        
        if n:
            
            print(n.key, ",", n.data, end="")
            
            if n.leftChild:
                self.display(n.leftChild,  "LEFT:   ",  indent + "    ")
            if n.rightChild:
                self.display(n.rightChild, "RIGHT:  ", indent + "    ")            
            
    
    
class FakeBallTree(object):
    
    #keeps track of all the (key, data) pairs
    def __init__(self, pairs):
        
        self.__pairs = pairs
        
    #finds exact key by brute force- looping through all the keys
    def findExact(self, key):
        
        for pair in self.__pairs:
            
            #if you find the key, return the data
            if pair[0]==key: return pair[1]
         
        #otherwise, return None   
        return None
    
    #finds k nearest neighbors by brute force
    def kNearestNeighbor(self, key, k):
        
        #if not enough elements, return them all
        if k > len(self.__pairs): return self.__pairs
        
        ans = []
        
        #put all keys in min heap based on distance from search key
        h = []
        
        #loop through all keys and push onto heap
        for pair in self.__pairs:
            dist = distance(key, pair[0])
            heapq.heappush(h,(dist,pair))
            
        #pop the k items with the smallest distance and return them as a list
        for i in range(k):
            
            item = heapq.heappop(h)
            ans += [item[1]] #isolate the pair
            
        return ans
            
            
            
            
        
        
def main():
    
    #create the pairs
    numDimensions = 5
    numPoints = 100
    pairs = []
    for i in range(numPoints):
        key = ()
        for j in range(numDimensions):
            key += (random.randint(1,100),)
            
        pairs += [(key,0)]
        
    #pairs = [((1,2),10),((4,5),32),((6,7),10),((10,12),10),((11,10),10)]
                   
    b = BallTree(pairs)
    b.display()
    print()
    print()
    
    f = FakeBallTree(pairs)
    
    print(b.findExact((1,2,3,4,5)))
    print(f.findExact((1,2,3,4,5)))
    
    print(b.kNearestNeighbor((52,55),3))
    print(f.kNearestNeighbor((52,55),3))
    
main()