from collections import Counter
from functools import reduce
from operator import add

from Graph_State_Machine.Util.generic_util import flatten, snd
from Graph_State_Machine.Util.misc import relevant_neighbours
from Graph_State_Machine.scores import presence_score

from typing import *
Step = Callable[[Any, List[str], str], List[Tuple[str, Any]]] # The 1st Any is Graph, but not imported for simplicity
    # Functions which order a Graph's nodes according to different criteria but with the overall goal of producing the
    # next logical step given a state (the set of already considered nodes)
Score = Callable[[List[str], List[str]], float]
    # Functions which compare two lists of nodes (e.g. the state and a given node's neighbours) and produce a numerical
    # score representing how similar/different they are. The framework treats higher values as better.



def by_score(score_function: Score = presence_score) -> Step:
    '''Produce a Step function which orders nodes by the given Score function'''
    def step_closure(Gr, state: List[str], node_type: str = None) -> List[Tuple[str, float]]:
        scores = [(n, score) for n in set(flatten(relevant_neighbours(Gr, state, node_type))) if (score := score_function(state, Gr.G.neighbors(n))) > 0]
        return sorted(scores, key = snd, reverse = True)
    return step_closure


def neighbour_intersection(Gr, state: List[str], node_type: str = None) -> List[Tuple[str, int]]:
    '''Order nodes by counts of presence in immediate state neighbours'''
    res_counts = reduce(add, [Counter(ns) for ns in relevant_neighbours(Gr, state, node_type)])
    return res_counts.most_common()


