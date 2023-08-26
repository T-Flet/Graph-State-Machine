from copy import deepcopy
import warnings
import networkx as nx
import matplotlib.pyplot as plt
from inspect import signature

from Graph_State_Machine.selectors import identity
from Graph_State_Machine.scanners import by_score
from Graph_State_Machine.updaters import list_accumulator, list_accumulator_greedy
from Graph_State_Machine.types import *
from Graph_State_Machine.Util.misc import expand_user_warning


class GSM:
    def __init__(self, graph: Graph, state: State = [],
                 node_scanner: Scanner = by_score(), state_updater: Updater = list_accumulator, selector = identity,
                 greedy_state_updater: Updater = list_accumulator_greedy):
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
        self.greedy_updater = greedy_state_updater

        self.log = [dict(method = '__init__', graph = graph, state = state, node_scanner = node_scanner,
                         state_updater = state_updater, list_accumulator = list_accumulator, selector = selector)]

    def __str__(self): return f'GSM State: {self.state.__str__()}'


    # Core functionality methods

    def extend_with(self, extension_graph, warn_about_problematic_sufficiencies = True):
        '''Note: returns a new object; does not affect the original'''
        res = deepcopy(self)
        res.graph = res.graph.extend_with(extension_graph, warn_about_problematic_sufficiencies)
        return res

    def _scan(self, *args, **kwargs) -> List[Tuple[Node, Any]]:
        '''Note: this method just returns the step result; it does not update the state'''
        return self.scanner(self.graph, self.selector(self.state), *args, **kwargs)

    def step(self, *args, conditional = False, greedy = False, **kwargs):
        '''Scan nodes of interest and perform a step (i.e. have the step_handler update the state by processing the scan result).
            If conditional == True, the step is performed only if no node of the requested type is in state.
                In that case an ASSUMPTION is made:
                that the first (named or unnamed) argument of scanner (after graph and state) is a singleton list of the type of node to look for.
            If greedy == True, then the step uses the self.greedy_updater updater (THE DEFAULT ONE IS ONLY FOR LIST-TYPE STATES), adding ALL candidates to state.'''
        if args and kwargs: raise TypeError('Step function arguments should be either all named or all unnamed (except for "conditional", which should always be named)')
        node_type = (args if args else (list(kwargs.values())))[0][0]
        if conditional and self.type_in_state(node_type):
            warnings.warn(f'Step of type \'{node_type}\' not taken because nodes of that type were already in state')
            return self
        else:
            def f():
                scan_result = self._scan(*args, **kwargs)
                self.log.append(dict(method = 'step', scan_result = scan_result, scanner_arguments = self._ensure_scanner_args_are_named(args, kwargs)))
                self.state, self.graph = (self.greedy_updater if greedy else self.updater)(self.state, self.graph, scan_result)
            expand_user_warning(f, lambda: f'; last log entry: {self.log[-1]}')
        return self

    def consecutive_steps(self, *scanners_arguments: List[Union[List, Dict]], conditional = False, greedy = False):
        '''Perform steps of the given node types one after the other, i.e. using the progressively updated state for each new step.
            Note: steps can be made either all standard or all conditional.'''
        for ss in scanners_arguments: self.step(**self._ensure_scanner_args_are_named(ss), conditional = conditional, greedy = greedy)
        return self

    def parallel_steps(self, *scanners_arguments: List[Union[List, Dict]], conditional = False, greedy = False):
        '''Perform steps of the given node types all starting from the same state, i.e. only apply state updates after scan results are known.
            Note: steps can be made either all standard or all conditional.'''
        scanners_arguments = [self._ensure_scanner_args_are_named(ss) for ss in scanners_arguments]
        scan_results = [self._scan(**ss) for ss in scanners_arguments]
        for rs, ss in zip(scan_results, scanners_arguments):
            node_type = list(ss.values())[0][0] # no list check because ss is already guaranteed to be a dictionary
            if conditional and self.type_in_state(node_type):
                warnings.warn(f'Step of type \'{node_type}\' not taken because nodes of that type were already in state')
                return self
            else:
                def f(): self.state, self.graph = (self.greedy_updater if greedy else self.updater)(self.state, self.graph, rs)
                expand_user_warning(f, lambda: f'; (parallel) step arguments: {ss}')
        self.log.append(dict(method = 'parallel_steps', scan_results = scan_results, scanners_arguments = scanners_arguments))
        return self


    # Plotting methods

    def plot(self, override_highlight: List[Node] = None,
             show_necessity = True, show_sufficiency = True,
             layout = nx.kamada_kawai_layout, layout_args: Dict[str, Any] = {},
             plotly = True, radial_labels = False, networkx_plot_args: Dict[str, Any] = {}):
        return self.graph.plot(override_highlight if override_highlight else self.selector(self.state), show_necessity, show_sufficiency, layout, layout_args, plotly, radial_labels, networkx_plot_args)


    # Utility methods

    def _ensure_scanner_args_are_named(self, ss: Union[List, Dict], otherwise_dict = None) -> Dict[str, Any]:
        '''If ss is not a dictionary of args, then line it up with the expected names and make it one; fallback to otherwise_dict if present'''
        return dict(zip(list(signature(self.scanner).parameters.keys())[2:], ss)) if ss and (isinstance(ss, list) or isinstance(ss, tuple)) else \
                otherwise_dict if otherwise_dict else ss

    def type_in_state(self, node_type: NodeType) -> bool: return node_type in self.graph.type_set(self.selector(self.state))


