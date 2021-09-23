from collections import Counter
from functools import reduce
from operator import add

from Graph_State_Machine.Util.generic_util import flatten
from Graph_State_Machine.Util.misc import relevant_neighbours
from Graph_State_Machine.scores import Score, jaccard_similarity
from Graph_State_Machine.types import *


def by_score(score_function: Score = jaccard_similarity) -> Scanner:
    '''Produce a Step function which orders nodes by the given Score function'''
    def scan_closure(graph: Graph, list_state: List[Node],
                     node_types: List[NodeType] = [], not_node_types: List[NodeType] = [],
                     neighbour_types: List[NodeType] = [], not_neighbour_types: List[NodeType] = []) -> List[Tuple[Node, float]]:
        '''NOTE: node_types and not_node_types govern which list_state nodes' neighbour to consider,
        while neighbour_types end not_neighbour_types do the same for the second order neighbours, i.e. the neighbours of the above neighbours.
        The utility of the latter pair is in including/excluding some node types when comparing the candidates neighbours with the current state'''
        if any(not isinstance(arg, list) for arg in [node_types, not_node_types, neighbour_types, not_neighbour_types]):
            raise TypeError(f'The arguments node_types, not_node_types, neighbour_types and not_neighbour_types should be lists of node types; received {node_types}, {not_node_types}, {neighbour_types} and {not_neighbour_types}')
        scores = [(n, score) for n in set(flatten(relevant_neighbours(graph, list_state, node_types, not_node_types)))
                    if (score := score_function(list_state, relevant_neighbours(graph, [n], neighbour_types, not_neighbour_types)[0])) > 0]
        return sorted(scores, key = lambda x: (-x[1], x[0]), reverse = False) # nested ordering: first by score, then by node name
    return scan_closure


def neighbour_intersection(graph: Graph, list_state: List[Node], node_types: List[NodeType] = [], not_node_types: List[NodeType] = []) -> List[Tuple[Node, int]]:
    '''Order nodes by counts of presence in immediate state neighbours'''
    res_counts = reduce(add, [Counter(ns) for ns in relevant_neighbours(graph, list_state, node_types, not_node_types)])
    return res_counts.most_common()


