import pytest
import math
import random

# Positive and negative infinity
PINF =  float('inf')
NINF = -float('inf')

# returns the distance between two points
def distance(p1, p2):
    dimensions = len(p1)
    sum = 0
    
    #calculate euclidean distance
    for i in range(dimensions):
        di = p1[i] - p2[i]
        sum += di**2
    
    return math.sqrt(sum)  

#returns the max distance between the center point and a list of child points
def maxDistance(center, pairs):

    radius = 0

    #for each point, if distance from center is greater than max, make it max
    for p in pairs:
        
        #the "point" is the key of the pair
        dist = distance(p[0],center[0]) 
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
            center = medianOfThree(pairs, DGS)
            print("center:",center)
         
            #separate the points into left and right
            leftPoints = []
            rightPoints = []
            
            #for each point, add to correct pile
            for pair in pairs:
                
                #leave out the center point
                if pair != center:
                    
                    #if the value at the DGS is <= center's, add to left
                    if pair[0][DGS] <= center[0][DGS]: leftPoints += [pair]
                
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
            #the distance from the center to the furthest child point
            maxLeft = maxDistance(center, leftPoints)
            maxRight = maxDistance(center, rightPoints)
            radius = max(maxLeft, maxRight)
                
            #create a Node with 2 children
            n = Node(center, leftChild, rightChild, radius)
        
        print("Node:", n.key, ",", n.data)
        return n
    
    
    #finds the data at this exact key
    #if key does not exist, returns None
    def findExact(self, key):
        
        return None
    
    
    #finds the k nearest neighbors to a specified point
    #returns a list of the neighbors' (key, data) pairs
    #if fewer than k points exist, return a list of all pairs
    def kNearestNeighbor(self, key, k):
        
        return None
    
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
    def __init__(self, numDimensions, pairs):
        
        self.__pairs = pairs
        
    #finds exact key by brute force- looping through all the keys
    def findExact(self, key):
        
        return None
    
    #finds k nearest neighbors by brute force- 
    #looping through all keys and keeping track of top k answers
    def kNearestNeighbor(self, key, k):
        
        return None
        
        
def main():
    
    #create the pairs
    numDimensions = 3
    numPoints = 10
    pairs = []
    for i in range(numPoints):
        key = ()
        for j in range(numDimensions):
            key += (random.randint(1,100),)
            
        pairs += [(key,0)]
        
    #pairs = [((1,2),0),((4,5),0),((6,7),0),((10,12),0),((11,10),0)]
                   
    b = BallTree(pairs)
    b.display()
    
main()