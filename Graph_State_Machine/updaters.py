
from Graph_State_Machine.types import *


def list_accumulator(state: State, graph: Graph, step_result: StepResult) -> Tuple[State, Graph]:
    '''Never removes from state and adds the highest scoring node from step_result to gsm.from_steps'''
    return state + [step_result[0][0]], graph


