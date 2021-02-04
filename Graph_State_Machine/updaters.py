from warnings import warn

from Graph_State_Machine.types import *


def list_accumulator(state: State, graph: Graph, scan_result: ScanResult) -> Tuple[State, Graph]:
    '''Never removes from state and adds the highest scoring node from step_result to gsm.from_steps'''
    if scan_result:  return state + [scan_result[0][0]], graph
    else:
        warn('A Scanner returned no result: no appropriate candidates identified')
        return state, graph


