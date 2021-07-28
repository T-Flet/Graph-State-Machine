from collections import Counter
from functools import reduce
from operator import add

from Graph_State_Machine.Util.generic_util import flatten
from Graph_State_Machine.Util.misc import relevant_neighbours
from Graph_State_Machine.scores import Score, jaccard_similarity
from Graph_State_Machine.types import *


def by_score(score_function: Score = jaccard_similarity) -> Scanner:
    '''Produce a Step function which orders nodes by the given Score function'''
    def scan_closure(graph: Graph, list_state: List[Node], node_type: NodeType = None) -> List[Tuple[Node, float]]:
        scores = [(n, score) for n in set(flatten(relevant_neighbours(graph, list_state, node_type))) if (score := score_function(list_state, list(graph.G.neighbors(n)))) > 0]
        return sorted(scores, key = lambda x: (-x[1], x[0]), reverse = False) # enforce alphabetical priority after score sorting
    return scan_closure


def neighbour_intersection(graph: Graph, list_state: List[Node], node_type: NodeType = None) -> List[Tuple[Node, int]]:
    '''Order nodes by counts of presence in immediate state neighbours'''
    res_counts = reduce(add, [Counter(ns) for ns in relevant_neighbours(graph, list_state, node_type)])
    return res_counts.most_common()


