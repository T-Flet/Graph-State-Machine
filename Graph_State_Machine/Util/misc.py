from collections import defaultdict

from Graph_State_Machine.types import *


def relevant_neighbours(Gr, state_list: List[str], node_type: NodeType = None) -> List[List[str]]:
    '''Return neighbours of state nodes of the requested type or all types if none specified'''
    return [[n for n in Gr.G.neighbors(sn) if not node_type or Gr.G.nodes[n][Gr.type_attr] == node_type] for sn in state_list]

def adjacencies_lossy_reverse(one_type_graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    '''Invert a dictionary of adjacencies, with possible losses e.g. {A: [B, C], D: []} -> {B: [A], C: [A]}'''
    reverse_subgraph = defaultdict(list)
    for v, to in one_type_graph.items():
        for t in to: reverse_subgraph[t].append(v)
    return reverse_subgraph

def strs_as_keys(strs: List[str], unique_value: List[str] = []) -> Dict[str, List[str]]:
    '''Make a dictionary with the given keys and all the values being the provided one'''
    return {t: unique_value for t in strs}


