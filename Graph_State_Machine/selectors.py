from functools import reduce
from operator import concat

from Graph_State_Machine.types import *


def identity(state: State) -> List[Node]: return state

def last_only(state: State) -> List[Node]: return [state[-1]]

def dict_fields_getter(dict_keys: List[str] = []) -> Selector:
    '''Note the different behaviour of the output functions from this constructor (intended for the Dict[str, List[Node]] State type) in these cases:
        - If any keys are given (including all of the available ones) the concatenation of their associated values will be returned
        - If NO keys are given then it will concatenate ALL values in the State dictionary, INCLUDING new fields which may be added later (not the case in the above)
    '''
    def selected_fields_closure(state: State) -> List[Node]: return list(reduce(concat, [state[k] for k in dict_keys]))
    def all_dict_fields_closure(state: State) -> List[Node]: return list(reduce(concat, state.values()))
    return selected_fields_closure if dict_keys else all_dict_fields_closure


