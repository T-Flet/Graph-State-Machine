import warnings
import networkx as nx
import numpy as np
from collections import defaultdict
from typing import *


def adjacencies_lossy_reverse(one_type_graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    '''Invert a dictionary of adjacencies, with possible losses e.g. {A: [B, C], D: []} -> {B: [A], C: [A]}'''
    reverse_subgraph = defaultdict(list)
    for v, to in one_type_graph.items():
        for t in to: reverse_subgraph[t].append(v)
    return reverse_subgraph

def strs_as_keys(strs: List[str], unique_value: List[str] = []) -> Dict[str, List[str]]:
    '''Make a dictionary with the given keys and all the values being the provided one'''
    return {t: unique_value for t in strs}


def expand_user_warning(f: Callable, suffix_f = lambda: ' <<-- nested warning'):
    with warnings.catch_warnings():  # Reset warning filter afterwards
        warnings.filterwarnings('error')
        res = None
        try: res = f()
        except Warning as w: # Append suffix if UserWarning
            warnings.filterwarnings('default')
            warnings.warn(w.args[0] + (suffix_f() if issubclass(w.__class__, UserWarning) else ''))
            return res
        except Exception as e: raise e # Raise other errors
        return res


def radial_degrees(x, y): return np.arctan2(y, x) * 180 / np.pi


