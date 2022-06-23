import warnings
import networkx as nx
import numpy as np
from collections import defaultdict
from warnings import warn
from typing import *


def check_edge_dict_keys(dict_many: Dict[str, List[str]]) -> None:
    ok_keys = ['necessary_for', 'sufficient_for', 'are_necessary', 'are_sufficient', 'plain']
    assert not (bad_keys := [k for k in dict_many.keys() if k not in ok_keys]), f'The only keys allowed in graph-shortand edge dictionaries are {ok_keys}; the following bad keys were provided: {bad_keys}'


def reverse_adjacencies(one_type_graph: Dict[str, List[str]], allow_losing_singletons = False, allow_losing_joint_sufficiency = False) -> Dict[str, List[str]]:
    '''Invert a dictionary of adjacencies, possibly losing singletons, e.g. {A: [B, C], D: []} -> {B: [A], C: [A]}'''
    if not allow_losing_singletons: assert not (singletons := [k for k, v in one_type_graph.items() if not v]), f'Singletons {singletons} loss prevented in reverse_adjacencies; set allow_losing_singletons to True to allow it (but check carefully first)'
    opposite = dict(are_necessary = 'necessary_for', are_sufficient = 'sufficient_for', necessary_for = 'are_necessary', sufficient_for = 'are_sufficient', plain = 'plain')

    reverse_subgraph = defaultdict(list)
    for start, ends in one_type_graph.items():
        if isinstance(ends, list):
            for end in ends: # Two-part check below because reverse_subgraph being a defaultdict(list) makes the 2nd part always True for new keys
                if end not in reverse_subgraph or isinstance(reverse_subgraph[end], list): reverse_subgraph[end].append(start)
                else: reverse_subgraph[end][opposite[edge_type]].append(start)
        else: # isinstance(ends, dict)
            check_edge_dict_keys(ends)

            pairs = [] # Unfortunately have to do this declare-then-fill pattern because twice-nested items could be lists requiring unpacking
            for edge_type, end in [(t, e) for t, es in ends.items() for e in es]:
                if isinstance(end, list):
                    if allow_losing_joint_sufficiency:
                        warn(f"Allowing lossy reversal of Node sub-list {end} in adjacency key '{edge_type}'; i.e. these edges will be plain when reversed; "
                             f"if these are intended joint sufficiencies, ensure they are declared on the '{start}' side; set allow_losing_joint_sufficiency to False to prevent this")
                        pairs += [('plain', e) for e in end]
                    else: raise ValueError(f"Within reverse_adjacencies, all the values within adjacency dictionaries need to be simple lists of Nodes (normally 'are_sufficient' is allowed sub-lists for joint sufficiency); "
                                           f"instead, '{start}''s '{edge_type}' contained the list {end}; "
                                           f"if these are intended joint sufficiencies, ensure they are declared on the '{start}' side; "
                                           f"set allow_losing_joint_sufficiency to True to allow lossy parsing (i.e. these edges will be plain when reversed here)")
                else: pairs.append((edge_type, end))

            for edge_type, end in pairs:
                if end not in reverse_subgraph: reverse_subgraph[end] = defaultdict(list)
                elif not isinstance(reverse_subgraph[end], dict): reverse_subgraph[end] = defaultdict(list, plain = reverse_subgraph[end])
                reverse_subgraph[end][opposite[edge_type]].append(start)

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


