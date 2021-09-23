
from Graph_State_Machine.graph import Graph, Node, NodeType, TypedAdjacencies

from typing import *

# These two can be anything as long as the user-defined Scanner and Updater functions can handle them
State = TypeVar('State')
ScanResult = TypeVar('StepResult')


Selector = Callable[[State], List[Node]]
    # Functions to extract from a State the list of nodes to perform a scan around

Scanner = Callable[[Graph, List[Node]], List[Tuple[Node, Any]]]
    # Functions which order a Graph's nodes according to different criteria but with the overall goal of producing the
    # next logical step given a state (the set of already considered nodes)
    # NOTE: arbitrary additional arguments, optional or required, may be present after Graph and List[Node],
    #           but there is no typing syntax to show this

Updater = Callable[[State, Graph, ScanResult], Tuple[State, Graph]]
    # Functions which update a GSM's state (and possibly graph) by processing the output of a step/scan method


