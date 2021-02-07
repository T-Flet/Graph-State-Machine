from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt

from Graph_State_Machine.selectors import identity
from Graph_State_Machine.scanners import by_score
from Graph_State_Machine.updaters import list_accumulator
from Graph_State_Machine.types import *


class GSM:
    def __init__(self, graph: Graph, state: State = [],
                 node_scanner: Scanner = by_score(), state_updater: Updater = list_accumulator, selector = identity):
        '''Define a Graph State Machine by providing the starting graph and state and the two operation functions:
            - the scanner, which assigns scores to nodes of interest given the state nodes (e.g. their neighbours)
            - the updater, which updates the state based on the scanner's output; it can update the graph too (though it does not have to)
        Note: if the type of state is not a list of strings then a function to produce one from it (for the purposes of giving Scanners a list of nodes to scan) has to be provided as the selector argument
        Note: the default GSM scores nodes by state presence in target neighbours, has a simple list as state and a simple appender as its updater
        '''
        self.graph = graph
        self.scanner = node_scanner

        self.state = state
        self.selector = selector
        self.updater = state_updater

    def __str__(self): return self.state.__str__()


    # Core functionality methods

    def extend_with(self, extension_graph):
        '''Note: returns a new object; does not affect the original'''
        res = deepcopy(self)
        res.graph = res.graph.extend_with(extension_graph)
        return res

    def _scan(self, node_type: NodeType = None) -> List[Tuple[Node, Any]]:
        '''Note: this method just returns the step result; it does not update the state'''
        return self.scanner(self.graph, self.selector(self.state), node_type)

    # def _scan_by_type(self, node_type: NodeType = None) -> Dict[NodeType, List[Tuple[Node, Any]]]:
    #     '''Note: this method just returns the step result; it does not update the state'''
    #     return {tp: self.scanner(self.graph, tp_ts, node_type) for tp, tp_ts in self.graph.group_tags(self.selector(self.state))}
    #     # Perhaps not used since can make the steps be grouped or not intrinsically;
    #     # would require transposer and sorter of transposed result to become a simple step again

    def step(self, node_type: NodeType = None):
        '''Scan nodes of interest and perform a step (i.e. have the step_handler update the state by processing the scan result)'''
        self.state, self.graph = self.updater(self.state, self.graph, self._scan(node_type))
        return self

    # def step_by_type(self):
    #     '''Scan nodes of interest and perform a step handling all different types of node separately (i.e. have the step_handler update the state by processing the scan result)'''
    #     self.state, self.graph = self.updater(self.state, self.graph, self._step_by_type_res())
    #     return self

    def consecutive_steps(self, node_types: List[NodeType]):
        '''Perform steps of the given node types one after the other, i.e. using the progressively updated state for each new step'''
        for nt in node_types: self.step(nt)
        return self

    def parallel_steps(self, node_types: List[NodeType]):
        '''Perform steps of the given node types all starting from the same state, i.e. only apply state updates after scan results are known'''
        scan_results = [self._scan(nt) for nt in node_types]
        for sr in scan_results: self.state, self.graph = self.updater(self.state, self.graph, sr)
        return self


    # Plotting methods

    def plot(self, override_highlight = None):
        return self.graph.plot(override_highlight if override_highlight else self.selector(self.state))


