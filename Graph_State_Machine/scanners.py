from collections import Counter
from functools import reduce
from operator import add

from Graph_State_Machine.Util.generic_util import flatten, snd
from Graph_State_Machine.Util.misc import relevant_neighbours
from Graph_State_Machine.scores import Score, presence_score
from Graph_State_Machine.types import *


def by_score(score_function: Score = presence_score) -> Scanner:
    '''Produce a Step function which orders nodes by the given Score function'''
    def step_closure(graph: Graph, list_state: List[str], node_type: NodeType = None) -> List[Tuple[str, float]]:
        scores = [(n, score) for n in set(flatten(relevant_neighbours(graph, list_state, node_type))) if (score := score_function(list_state, graph.G.neighbors(n))) > 0]
        return sorted(scores, key = snd, reverse = True)
    return step_closure


def neighbour_intersection(graph: Graph, list_state: List[str], node_type: NodeType = None) -> List[Tuple[str, int]]:
    '''Order nodes by counts of presence in immediate state neighbours'''
    res_counts = reduce(add, [Counter(ns) for ns in relevant_neighbours(graph, list_state, node_type)])
    return res_counts.most_common()


