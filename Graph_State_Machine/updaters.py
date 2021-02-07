from warnings import warn
from copy import deepcopy

from Graph_State_Machine.types import *


def list_accumulator(state: State, graph: Graph, scan_result: ScanResult) -> Tuple[State, Graph]:
    '''Never removes from state and adds the highest scoring node from step_result to a simple-list state'''
    if scan_result:  return state + [scan_result[0][0]], graph
    else:
        warn('A Scanner returned no result: no appropriate candidates identified')
        return state, graph


def list_in_dict_accumulator(dict_key: str) -> Updater:
    def dict_accumulator_closure(state: State, graph: Graph, scan_result: ScanResult) -> Tuple[State, Graph]:
        f'''Never removes from state and adds the highest scoring node from step_result to the {dict_key} field of the state dictionary'''
        if scan_result:
            new_state = deepcopy(state)
            new_state[dict_key].append(scan_result[0][0])
            return new_state, graph
        else:
            warn('A Scanner returned no result: no appropriate candidates identified')
            return state, graph
    return dict_accumulator_closure


