import networkx as nx
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from copy import deepcopy

from Graph_State_Machine.Util.generic_util import diff, group_by
import Graph_State_Machine.steps as ss

from typing import *
TypedAdjacencies = Dict[str, Dict[str, List[str]]]
Step = Callable[[Any, List[str], str], List[Tuple[str, Any]]] # The 1st Any is Graph, but not imported for simplicity
_a = TypeVar('_a')


class Graph:
    def __init__(self, G: Union[nx.Graph, TypedAdjacencies], step_func: Step = ss.neighbour_intersection, type_attr: str = 'node_type'):
        '''Note: the constructor accepts either a Networkx Graph or a Dict[str, Dict[str, List[str]]] (aliased to TypedAdjacencies internally).
        Calling the constructor with the latter is equivalent to Graph(Graph.read_typed_adjacency_list(TypedAdjacencies_OBJECT, type_attr), type_attr)'''
        self.type_attr = type_attr
        self.default_cols = None
        self.colour_map = None

        if not isinstance(G, nx.Graph): G = Graph.read_typed_adjacency_list(G, self.type_attr)
        self._set_graph(G)

        self.step_func = step_func # MOVE TO STATE INSTEAD?


    # Init-related methods

    def _set_graph(self, G: nx.Graph):
        self.G = G
        self.consistent()

        self.nodes_to_types = self._get_nodes_to_types()
        self.types = sorted(list(set(nx.get_node_attributes(self.G, self.type_attr).values())))

        self._set_colours()
        return self

    @staticmethod
    def read_typed_adjacency_list(tas: TypedAdjacencies, type_attr: str = 'node_type') -> nx.Graph:
        G = nx.Graph()
        for nt, one_to_many in tas.items(): G.add_nodes_from(one_to_many.keys(), **{type_attr: nt})
        for nt, one_to_many in tas.items(): G.add_edges_from([(start, end) for start, many in one_to_many.items() for end in many])
        return G

    def consistent(self):
        typed_ns = set(nx.get_node_attributes(self.G, self.type_attr).keys())
        assert set(self.G.nodes) == typed_ns, f'Some nodes have no type: {set(self.G.nodes) - typed_ns}'
        return self

    def _get_nodes_to_types(self) -> Dict[str, str]: return nx.get_node_attributes(self.G, self.type_attr)

    def _set_colours(self, custom_cols = None):
        xkcd_palette = ['xkcd:green', 'xkcd:blue', 'xkcd:purple', 'xkcd:red', 'xkcd:orange', 'xkcd:yellow', 'xkcd:lime', 'xkcd:teal', 'xkcd:azure']
        # ms_office_dark_theme_palette = {'Green': '#81BB42', 'Blue': '#4A9BDC', 'Red': '#DF2E28', 'Orange': '#FE801A', 'Yellow': '#E9BF35', 'Cyan': '#32C7A9', 'Dark Orange': '#D15E01'}.values()
        xkcd_palette = xkcd_palette + diff(mcolors.XKCD_COLORS.keys(), xkcd_palette)

        if self.colour_map:
            if set(self.colour_map.keys()) != set(self.types): # Nothing to change if equal
                new_types = diff(self.types, self.colour_map.keys())
                new_cols = diff(self.default_cols, self.colour_map.values())
                new_map = dict(zip(new_types, new_cols))
                # The following two are defined so as to look as though they were defined directly and not from an extension
                self.colour_map = {t: self.colour_map[t] if t in self.colour_map else new_map[t] for t in self.types}
                self.default_cols = list(self.colour_map.values()) + diff(self.default_cols, self.colour_map.values())
        else:
            if custom_cols: self.default_cols = custom_cols + diff(xkcd_palette, custom_cols)
            elif self.default_cols: self.default_cols = self.default_cols + diff(xkcd_palette, self.default_cols)
            else: self.default_cols = xkcd_palette
            self.colour_map = dict(zip(self.types, self.default_cols))
        return self


    # Core functionality methods

    def group_tags(self, tags: List[str]) -> Dict[str, List[str]]: return group_by(lambda t: self.nodes_to_types[t], tags)

    def step(self, state: List[str], node_type: str = None) -> List[Tuple[str, Any]]:
        assert (ord_res := self.step_func(self, state, node_type)), 'No suitable successor state exists'
        return ord_res

    def step_by_type(self, state: List[str], node_type: str = None) -> Dict[str, List[Tuple[str, Any]]]: # Dict for now
        return {tp: self.step_func(self, tp_ts, node_type) for tp, tp_ts in self.group_tags(state)}
        # Perhaps not used since can make the steps be grouped or not intrinsically;
        # would require transposer and sorter of transposed result to become a simple step again

    def extend_with(self, extension_graph):
        '''Note: returns a new object; does not affect the original'''
        res = deepcopy(self)
        return res._set_graph(nx.compose(res.G, extension_graph.G))


    # Plotting methods

    def get_node_colours(self) -> List[str]:
        return [self.colour_map[u[1]] for u in self.G.nodes(data = self.type_attr)]

    def plot(self, state: List[str] = None): # In the future find a way to highlight state nodes
        if not state:
            nx.draw_kamada_kawai(self.G, arrows = True, with_labels = True, node_color = self.get_node_colours())
            # The following is a networkx-matplotlib hack to print a colour legend: use empty scatter plots
            for t, c in self.colour_map.items(): plt.scatter([], [], c = [c], label = t)
            plt.legend()
            plt.show()


