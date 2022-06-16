from collections import Counter
from functools import reduce
from operator import add

from Graph_State_Machine.Util.generic_util import flatten
from Graph_State_Machine.scores import Score, jaccard_similarity
from Graph_State_Machine.types import *


def by_score(score_function: Score = jaccard_similarity, check_only_state_types = False, check_necessity = True, check_sufficiency = True) -> Scanner:
    '''Produce a Step function which orders nodes by the given Score function;
        can also provide the default values of Scanner parameters which can be deviated from individually on each GSM.step call.

        Setting check_only_state_types to True restricts the attention when examining the neighbours of candidate nodes solely on
        those of types present in the state (in terms of parameters of the returned closure it overrides neighbour_types
        and bad_neighbour_types with the graph.state_types() and None)'''
    def scan_closure(graph: Graph, list_state: List[Node],
                     candidate_types: List[NodeType] = None, bad_candidate_types: List[NodeType] = None,
                     neighbour_types: List[NodeType] = None, bad_neighbour_types: List[NodeType] = None,
                     check_only_state_types = check_only_state_types,
                     check_necessity = check_necessity, check_sufficiency = check_sufficiency) -> List[Tuple[Node, float]]:
        '''candidate_types and bad_candidate_types govern which list_state nodes' neighbour to consider,
            while neighbour_types end bad_neighbour_types do the same for the second order neighbours, i.e. the neighbours of the above neighbours.
            The utility of the latter pair is in including/excluding some node types when comparing the candidates' neighbours with the current state.

            Setting check_only_state_types to True restricts the attention when examining the neighbours of candidate nodes solely on
            those of types present in the state (in terms of parameters of the returned closure it overrides neighbour_types
            and bad_neighbour_types with the graph.state_types() and None)'''
        if any(bad_args := {arg: v for arg, v in dict(candidate_types = candidate_types, bad_candidate_types = bad_candidate_types, neighbour_types = neighbour_types, bad_neighbour_types = bad_neighbour_types).items() if v is not None and not isinstance(v, list)}):
            raise TypeError(f'The following arguments should be lists of node types but received these values: {bad_args}')

        candidates = set(flatten(graph.relevant_neighbours(list_state, candidate_types, bad_candidate_types)))
        if check_necessity or check_sufficiency: candidates = graph.necessity_sufficiency_filter(list_state, candidates, check_necessity, check_sufficiency, check_only_state_types)
        if check_only_state_types: neighbour_types, bad_neighbour_types = graph.type_set(list_state), None
        scores = [(c, score) for c in candidates
                  if (score := score_function(list_state, graph.relevant_neighbours([c], neighbour_types, bad_neighbour_types)[0])) > 0]
        return sorted(scores, key = lambda x: (-x[1], x[0]), reverse = False) # nested ordering: first by score, then by node name
    return scan_closure


def neighbour_intersection(graph: Graph, list_state: List[Node],
                           candidate_types: List[NodeType] = None, bad_candidate_types: List[NodeType] = None,
                           neighbour_types: List[NodeType] = None, bad_neighbour_types: List[NodeType] = None,
                           check_necessity = True, check_sufficiency = True) -> List[Tuple[Node, int]]:
    '''Order nodes by counts of presence in immediate state neighbours
        (standard candidate and neighbour type filters apply, with the latter acting directly on nodes in list_state in this Scanner)'''
    if any(bad_args := {arg: v for arg, v in dict(candidate_types = candidate_types, bad_candidate_types = bad_candidate_types, neighbour_types = neighbour_types, bad_neighbour_types = bad_neighbour_types).items() if v is not None and not isinstance(v, list)}):
        raise TypeError(f'The following arguments should be lists of node types but received these values: {bad_args}')

    filtered_state = graph.type_filter(list_state, neighbour_types, bad_neighbour_types) # The state nodes ARE the totality of neighbours in this Scanner
    res_counts = reduce(add, [Counter(ns) for ns in graph.relevant_neighbours(filtered_state, candidate_types, bad_candidate_types)])
    if check_necessity or check_sufficiency:
        ok_candidates = graph.necessity_sufficiency_filter(filtered_state, res_counts.keys(), check_necessity, check_sufficiency)
        for c in set(res_counts.keys()).difference(ok_candidates): del res_counts[c]
    return res_counts.most_common()


