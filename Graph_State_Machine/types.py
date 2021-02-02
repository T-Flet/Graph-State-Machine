
from Graph_State_Machine.graph import Graph, NodeType, TypedAdjacencies

from typing import *

# These two can be anything as long as the user-defined Scanner and Updater functions can handle them
State = TypeVar('State')
StepResult = TypeVar('StepResult')

Scanner = Callable[[Graph, State, NodeType], List[Tuple[str, Any]]]
    # Functions which order a Graph's nodes according to different criteria but with the overall goal of producing the
    # next logical step given a state (the set of already considered nodes)

Updater = Callable[[State, Graph, StepResult], Tuple[State, Graph]]
    # Functions which update a GSM's state (and possibly graph) by processing the output of a step/scan method


