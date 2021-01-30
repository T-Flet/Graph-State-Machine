import random
import string

from collections import defaultdict
from typing import *


def relevant_neighbours(Gr, state: List[str], node_type: str = None) -> List[List[str]]:
    return [[n for n in Gr.G.neighbors(sn) if not node_type or Gr.G.nodes[n][Gr.type_attr] == node_type] for sn in state]


def random_string(n = 8):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(n))

def pretty_num(num): return '{:+.2e}'.format(num)



def adjacencies_lossy_reverse(one_type_graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    reverse_subgraph = defaultdict(list)
    for v, to in one_type_graph.items():
        for t in to: reverse_subgraph[t].append(v)
    return reverse_subgraph

def strs_as_keys(strs: List[str], unique_value: List[str] = []) -> Dict[str, List[str]]: return {t: unique_value for t in strs}


