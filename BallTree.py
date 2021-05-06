import pytest
import math
import random
import heapq
import time

# Positive and negative infinity
PINF =  float('inf')
NINF = -float('inf')

# returns the distance between two points
def distance(p1, p2):
    
    #if points are in different dimensions, use greater number of dimensions
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
            #print("pairs:",pairs)
            #print("DGS:", DGS)
                    
            #choose a central point considering the DGS
            pivot = medianOfThree(pairs, DGS)
            #print("pivot:",pivot)
         
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
                
            #print("left points:", leftPoints)
            #print("right points:", rightPoints)
                
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
        
        #print("Node:", n.key, ",", n.data)
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
    #if k <= 0, return None
    def kNearestNeighbor(self, key, k, n='start', heap=None):
        
        if k > 0:
        
            #start with the root
            if n == 'start': 
                n = self.__root
                
                #initialize max heap as infinity
                #keep heap values negative to make it a max heap (default is min)
                heap = [(NINF,None,None)]
            
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
                    
            
                #recurse into children
                #will decide whether to go further at beginning of function
                self.kNearestNeighbor(key, k, n.leftChild, heap)
                self.kNearestNeighbor(key, k, n.rightChild, heap)
             
             
            #isolate the key,data pairs
            #don't include the None placeholder if it's there (weren't enough points)
            return [(i[1],i[2]) for i in heap if i[1]]
            
        
    
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
        
        if k > 0:
        
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
    
    
#utility method: makes a list of random points with specified 
#size of list and number of dimensions
def makePairs(size, d):
    
    pairs = []

    #for each pair, make random key d dimensions long with random data
    for i in range(size):
        key = ()
        for j in range(d): key += (random.random(),)                
        data = random.random() 
        pairs += [(key,data)]    
        
    return pairs
            
            
                   
        
def __main():
    
    ##create the pairs
    #numDimensions = 5
    #numPoints = 100
    #pairs = []
    #for i in range(numPoints):
        #key = ()
        #for j in range(numDimensions):
            #key += (random.randint(1,100),)
            
        #pairs += [(key,0)]
        
    ##pairs = [((1,2),10),((4,5),32),((6,7),10),((10,12),10),((11,10),10)]
                   
    #b = BallTree(pairs)
    #b.display()
    #print()
    #print()
    
    #f = FakeBallTree(pairs)
    
    #print(b.findExact((1,2,3,4,5)))
    #print(f.findExact((1,2,3,4,5)))
    
    #print(b.kNearestNeighbor((52,55,6,7),3))
    #print(f.kNearestNeighbor((52,55,4,5),3))
    
    #compare run times of real and fake BT
    
    pairs = makePairs(100000,5)
    
    start = time.time()
    b = BallTree(pairs)
    end = time.time()
    print("build time:", end-start)
    f = FakeBallTree(pairs)
    
    start = time.time()
    b.findExact((1,2,3))
    end = time.time()
    print("real search time:", end-start)
    
    start = time.time()
    f.findExact((1,2,3))
    end = time.time()
    print("fake search time:", end-start)    
    
    start = time.time()
    b.kNearestNeighbor((.1,.4,.2,.3,.4),10)
    end = time.time()
    print("real KNN time:", end-start)
    
    start = time.time()
    f.kNearestNeighbor((.1,.4,.2,.3,.4),10)
    end = time.time()
    print("fake KNN time:", end-start)    
    
    
    
#if __name__ == '__main__':
    #__main() 
    
#PYTESTS

#build trees of various sizes and dimensions 
#and check that all points can be found

#tree with one pair in 1D
def test_findOne1D():
    pairs = makePairs(1, 1)
    b = BallTree(pairs)
    f = FakeBallTree(pairs)
    assert b.findExact(pairs[0][0]) == f.findExact(pairs[0][0]) == pairs[0][1]
    
#tree with one pair in 2D
def test_findOne2D():
    pairs = makePairs(1, 2)
    b = BallTree(pairs)
    f = FakeBallTree(pairs)
    assert b.findExact(pairs[0][0]) == f.findExact(pairs[0][0]) == pairs[0][1]
    
#tree with one pair in 3+ D
def test_findOneMultD():
    #3-6 dimensions
    for d in range(3,7):
        pairs = makePairs(1, d)
        b = BallTree(pairs)
        f = FakeBallTree(pairs)
        assert b.findExact(pairs[0][0]) == f.findExact(pairs[0][0]) == pairs[0][1]
        
#small trees
def test_findSmall():
    
    #sizes from 3-5
    for size in range(3,6):
        
        #1-6 dimensions
        for d in range(1,7):
            
            pairs = makePairs(size, d)
            b = BallTree(pairs)
            f = FakeBallTree(pairs)
            
            #loop through each key and see if it can be found
            for pair in pairs:
                assert b.findExact(pair[0]) == f.findExact(pair[0]) == pair[1]
            

#various sizes from 10-100
def test_findMedium():
    
    #sizes from 10-100
    for size in range(10, 110, 10):
        
        #1-6 dimensions
        for d in range(1,7):
            
            pairs = makePairs(size, d)
            b = BallTree(pairs)
            f = FakeBallTree(pairs)
            
            #loop through each key and see if it can be found
            for pair in pairs:
                assert b.findExact(pair[0]) == f.findExact(pair[0]) == pair[1]
                
#size from 1000-10000 (only choose one size for the sake of time)
def test_findLarge():
    
    size = random.randint(1000,10000)
        
    #1-6 dimensions
    for d in range(1,7):
        
        pairs = makePairs(size, d)
        b = BallTree(pairs)
        f = FakeBallTree(pairs)
        
        #loop through each key and see if it can be found
        for pair in pairs:
            assert b.findExact(pair[0]) == f.findExact(pair[0]) == pair[1]
                
#create very large tree
def test_findVeryLarge():
    
    size = 100000
    d = 3
    
    pairs = makePairs(size, d)
    b = BallTree(pairs)
    
    #search for 5 random keys
    for i in range(5):
        pair = random.choice(pairs)
        assert b.findExact(pair[0]) == pair[1] 
        
#search for a key that will definitely not be found
def test_notFound():
    
    #sizes from 10-100
    for size in range(10, 110, 10):
        
        #1-6 dimensions
        for d in range(1,7):
            
            pairs = makePairs(size, d)
            b = BallTree(pairs)
            f = FakeBallTree(pairs)
            
            #look for a key that is not there
            assert b.findExact((1.1,1.2,1.3)) == f.findExact((1.1,1.2,1.3)) == None
         
                
#tests for k nearest neighbor

#simplest: 1 point, 1 neighbor, 1D
def test_KNNsimple():
    pairs = makePairs(1, 1)
    b = BallTree(pairs)
    f = FakeBallTree(pairs)
    searchKey = (random.random(),)
    assert b.kNearestNeighbor(searchKey, 1) == f.kNearestNeighbor(searchKey, 1)
    
#1 pt, 1 neighbor, multiple dimensions
def test_KNNMultD():
    for d in range(2,7):
        pairs = makePairs(1, d)
        b = BallTree(pairs)
        f = FakeBallTree(pairs)    
        searchKey = ()
        for j in range(d): searchKey += (random.random(),)
        assert b.kNearestNeighbor(searchKey, 1) == f.kNearestNeighbor(searchKey, 1)
        
#k=1
def test_KNN1neighbor():
    
    #medium sized trees
    for size in range(10, 110, 10):
        
        #1-6 dimensions
        for d in range(1,7):
            
            pairs = makePairs(size, d)
            b = BallTree(pairs)
            f = FakeBallTree(pairs)
            
            #search for 1 nearest neighbor
            searchKey = ()
            for j in range(d): searchKey += (random.random(),)
            assert b.kNearestNeighbor(searchKey, 1) == f.kNearestNeighbor(searchKey, 1)   
            
#small k
def test_KNNfew():
    
    #medium sized trees
    for size in range(20, 110, 10):
        
        #1-6 dimensions
        for d in range(1,7):
            
            pairs = makePairs(size, d)
            b = BallTree(pairs)
            f = FakeBallTree(pairs)
            
            #search for 2-20 nearest neighbors
            for k in range(2, 21):
                searchKey = ()
                for j in range(d): searchKey += (random.random(),)
                ans1 = b.kNearestNeighbor(searchKey, k)
                ans2 = f.kNearestNeighbor(searchKey, k)
                ans1.sort()
                ans2.sort()
                assert ans1 == ans2
                
#large k
def test_KNNmany():
    
    size = 1000
        
    #3-5 dimensions
    for d in range(3,6):
        
        pairs = makePairs(size, d)
        b = BallTree(pairs)
        f = FakeBallTree(pairs)
        
        #search for 100-1000 nearest neighbors
        for k in range(100, 1000, 9):
            searchKey = ()
            for j in range(d): searchKey += (random.random(),)
            ans1 = b.kNearestNeighbor(searchKey, k)
            ans2 = f.kNearestNeighbor(searchKey, k)
            ans1.sort()
            ans2.sort()
            assert ans1 == ans2 
            
#k > size
def test_KNNtooMany():
    
    size = 20
    d = 3
    
    pairs = makePairs(size, d)
    b = BallTree(pairs)
    f = FakeBallTree(pairs)
    
    #search for 25-30 nearest neighbors
    for k in range(25, 31):
        searchKey = ()
        for j in range(d): searchKey += (random.random(),)
        ans1 = b.kNearestNeighbor(searchKey, k)
        ans2 = f.kNearestNeighbor(searchKey, k)
        ans1.sort()
        ans2.sort()
        assert ans1 == ans2 
        
#search for 0 neighbors
def test_KNNnone():
    
    size = 20
    d = 3
    
    pairs = makePairs(size, d)
    b = BallTree(pairs)
    f = FakeBallTree(pairs)
    
    #search for 0 nearest neighbors
    searchKey = ()
    for j in range(d): searchKey += (random.random(),)
    ans1 = b.kNearestNeighbor(searchKey, 0)
    ans2 = f.kNearestNeighbor(searchKey, 0)
    assert ans1 == ans2 == None
        
def test_torture():
    
    #10 trees of random size and d
    for i in range(10):
        size = random.randint(1,1000)
        d = random.randint(1,7)
        pairs = makePairs(size, d)
        b = BallTree(pairs)
        f = FakeBallTree(pairs)
        
        #search for 5 random keys
        for i in range(5):
            pair = random.choice(pairs)
            assert b.findExact(pair[0]) == f.findExact(pair[0]) == pair[1]  
            
        #search for knn
        k = random.randint(1,100)
        searchKey = ()
        for j in range(d): searchKey += (random.random(),)
        ans1 = b.kNearestNeighbor(searchKey, k)
        ans2 = f.kNearestNeighbor(searchKey, k)
        ans1.sort()
        ans2.sort()
        assert ans1 == ans2         


pytest.main(["-v", "-s", "BallTree.py"]) 