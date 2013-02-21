'''
    Few notes:
        TODO(srvasude): Make more efficient by generating possible moves solely from connections between connected components.
        TODO(srvasude): Possibly decrease storage space of Node class.
'''
import itertools
from collections import defaultdict
from copy import deepcopy
import sys
# The list of all the triangles
tri_location = defaultdict(list)
class Node:
    def __init__(self,n):
        # Edges that have not been colored
        self.uncolored = set(itertools.combinations(range(1,n+1),2))
        # Edges that have been colored red
        self.red = set()
        # Edges that have been colored blue
        self.blue = set()
        self.fringe = set()
        self.conn_components = list()
    # Returns the vertices of a list of edges. Useful for shifting to a more efficient version
    def vertices(self,component):
        return set(item for tupl in component for item in tupl)
    # Color an edge (red =1. blue=-1) and return 1 if a triangle has been created
    def color(self,edge,flag=1):
        self.uncolored.remove(edge)
        meld = []
        for v in edge:
            for comp in self.conn_components:
                if v in self.vertices(comp):
                    comp.add(edge)
                    self.conn_components.remove(comp)
                    meld.append(comp)
        if not meld:
            st = set()
            st.add(edge)
            self.conn_components.append(st)
        else:
            new_comp = set.union(*meld)
            self.conn_components.append(new_comp)
        self.fringe.discard(edge)
        self.fringe.update(filter(lambda x: edge[0] in x or edge[1] in x, self.uncolored))
        if flag == 1:
            self.red.add(edge)
            for pair_edge in tri_location[edge]:
                if pair_edge[0] in self.red and pair_edge[1] in self.red:
                    return 1
        else:
            self.blue.add(edge)
            for pair_edge in tri_location[edge]:
                if pair_edge[0] in self.blue and pair_edge[1] in self.blue:
                    return 1
        return 0
#TODO: Every step add to a connected component
#Yield an edge to be colored flip (red=1,blue=-1) and the corresponding child
#Don't yield anything if the player inadvertently creates a triangle of their color
def gen_children(node,flip):
    new_elem = node.uncolored - node.fringe
    if new_elem:
        cpy = deepcopy(node)
        edge = new_elem.pop()
        ret = cpy.color(edge,flip)
        if not ret:
            yield cpy
    for edge in node.fringe:
        cpy = deepcopy(node)
        ret = cpy.color(edge,flip)
        if ret: 
            continue
        yield cpy
#Finds minimax value,using negamax + alpha/beta
#MAYBE: Remove list generation?
#TODO: Find some way to convert this to a playable algorithm?
def negamax(node,alpha,beta,flip=1):
    val = -20
    if not node.uncolored:
        # No moves, so there must be a draw game
        return 0
    # Used generator as there could be simple way of checking no new children
    for child in gen_children(node,flip):
        # The list of moves to get to optimal state, and value of state
        val = -negamax(child,-beta,-alpha,-flip)
        # The score is of our opponent, so we negate it
        if val >= beta:
            return val
        if val >= alpha:
            alpha = val
    # No new children, meaning player must place a triangle of their own color
    if val == -20:
        return -1
    return alpha
# Initialize the triangles
for tri in itertools.combinations(range(1,int(sys.argv[1])+1), 3):
    edge_1 = (tri[0],tri[1])
    edge_2 = (tri[1],tri[2])
    edge_3 = (tri[0],tri[2])
    # Now add these triangles to the index
    tri_location[edge_1].append((edge_2,edge_3)) 
    tri_location[edge_2].append((edge_1,edge_3)) 
    tri_location[edge_3].append((edge_1,edge_2)) 

# Doesn't matter where first player starts.
# TODO: remove this when playing is optimized
starting = Node(int(sys.argv[1]))
starting.color((1,2),1)
val = -negamax(starting,-1,1,-1)
print 'Not colored:',starting.uncolored, '\033[31mRed:\033[0m',starting.red,'\033[34mBlue\033[0m',starting.blue  
if val == 1:
    print "1st player has a winning strategy"
elif val == -1:
    print "2nd player has a winning strategy"
else:
    print "Optimal play leads to draw"

