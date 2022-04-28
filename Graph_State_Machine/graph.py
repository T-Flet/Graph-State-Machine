import networkx as nx
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from copy import deepcopy

from Graph_State_Machine.Util.generic_util import diff, group_by, flatten, intersperse_val
from Graph_State_Machine.Util.misc import radial_degrees

from typing import *
Node = str
NodeType = str
TypedAdjacencies = Dict[NodeType, Dict[Node, List[Node]]]


class Graph:
    def __init__(self, G: Union[nx.Graph, TypedAdjacencies], type_attr: NodeType = 'node_type'):
        '''Note: the constructor accepts either a Networkx Graph or a Dict[NodeType, Dict[Node, List[Node]]] (aliased to TypedAdjacencies internally).
        Calling the constructor with the latter is equivalent to Graph(Graph.read_typed_adjacency_list(TypedAdjacencies_OBJECT, type_attr), type_attr)'''
        self.type_attr = type_attr
        self.default_cols = None
        self.colour_map = None

        if not isinstance(G, nx.Graph): G = Graph.read_typed_adjacency_list(G, self.type_attr)
        self._set_graph(G)


    # Init-related methods

    def _set_graph(self, G: nx.Graph):
        self.G = G
        self.consistent()

        self.nodes_to_types = self._get_nodes_to_types()
        self.types = sorted(list(set(nx.get_node_attributes(self.G, self.type_attr).values())))

        self._set_colours()
        return self

    @staticmethod
    def read_typed_adjacency_list(tas: TypedAdjacencies, type_attr: NodeType = 'node_type') -> nx.Graph:
        G = nx.Graph()
        for nt, one_to_many in tas.items(): G.add_nodes_from(one_to_many.keys(), **{type_attr: nt})
        for nt, one_to_many in tas.items(): G.add_edges_from([(start, end) for start, many in one_to_many.items() for end in many])
        return G

    def consistent(self):
        typed_ns = set(nx.get_node_attributes(self.G, self.type_attr).keys())
        assert set(self.G.nodes) == typed_ns, f'Some nodes have no type: {set(self.G.nodes) - typed_ns}'
        return self

    def _get_nodes_to_types(self) -> Dict[Node, NodeType]: return nx.get_node_attributes(self.G, self.type_attr)

    def _set_colours(self, custom_cols = None):
        xkcd_palette = ['xkcd:green', 'xkcd:blue', 'xkcd:purple', 'xkcd:red', 'xkcd:orange', 'xkcd:yellow', 'xkcd:lime', 'xkcd:teal', 'xkcd:azure']
        # ms_office_dark_theme_palette = {'Green': '#81BB42', 'Blue': '#4A9BDC', 'Red': '#DF2E28', 'Orange': '#FE801A', 'Yellow': '#E9BF35', 'Cyan': '#32C7A9', 'Dark Orange': '#D15E01'}.values()
        xkcd_palette = xkcd_palette + diff(mcolors.XKCD_COLORS.keys(), xkcd_palette)
        # Removing some colours which are very similar to the hardcoded first few
        xkcd_palette = diff(xkcd_palette, ['xkcd:dark grass green', 'xkcd:dark pastel green', 'xkcd:fresh green', 'xkcd:electric lime', 'xkcd:light eggplant'])

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

    def group_nodes(self, nodes: List[Node]) -> Dict[NodeType, List[Node]]:
        unsorted = group_by(lambda n: self.nodes_to_types[n], nodes)
        return {nt: unsorted[nt] for nt in sorted(unsorted)}

    def extend_with(self, extension_graph):
        '''Note: returns a new object; does not affect the original'''
        res = deepcopy(self)
        return res._set_graph(nx.compose(res.G, extension_graph.G))


    # Utility methods

    def nodes_of_types(self, nodes: List[Node] = None, node_types: List[NodeType] = None,
                       not_node_types: List[NodeType] = None) -> Dict[NodeType, List[Node]]:
        '''Returns the given nodes (or all the graph nodes) filtered and grouped by their type'''
        good_types = set(node_types if node_types else self.types)
        if not_node_types: good_types = good_types.difference(not_node_types)
        # return {nt: [n for n in (nodes if nodes else Gr.G.nodes) if Gr.G.nodes[n][Gr.type_attr] == nt] for nt in good_types} # not using cached types
        return {nt: ns for nt, ns in self.group_nodes(nodes if nodes else self.G.nodes).items() if nt in good_types}

    # The core filtering in relevant_neighbours overlaps a bit with that in nodes_of_types, but it would not be
    #   as efficient to use the latter in the former (cannot benefit from caching the node_types since state neighbours can have
    #   different sets of types, then would need to get dictionary values and flatten them, etc)
    def relevant_neighbours(self, nodes: List[Node], node_types: List[NodeType] = None,
                            not_node_types: List[NodeType] = None) -> List[List[Node]]:
        '''Return neighbours of state nodes of the specified types or all types if none specified'''
        return [[n for n in self.G.neighbors(sn) if (t := self.G.nodes[n][self.type_attr])
                 if not node_types or t in node_types if not not_node_types or t not in not_node_types] for sn in nodes]


    # Plotting methods

    def get_node_colours(self, nodes_with_outline = None) -> Tuple[List[str], List[str]]:
        cols = [self.colour_map[u[1]] for u in self.G.nodes(data = self.type_attr)] # Not pattern-matching the pair for consistency with u below
        if nodes_with_outline:
            outs = ['#606060' if u[0] in nodes_with_outline else c for u, c in zip(self.G.nodes(data = self.type_attr), cols)]
            return cols, outs
        else: return cols, cols

    def plot(self, nodes_with_outline: List[Node] = None,
             layout: Callable[[Any], Dict[Any, Iterable[float]]] = nx.kamada_kawai_layout, layout_args: Dict[str, Any] = {},
             plotly = True, radial_labels = False, networkx_plot_args: Dict[str, Any] = {}):
        '''Plots the GSM graph either through plotly or networkx.
            - layout and layout_args are always used
            - networkx_plot_args is only used if plotly is False; reference for its content: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html .
            - radial_labels is only used if plotly is True, and is intended for use with the nx.shell_layout layout
        '''
        coords = layout(self.G, **layout_args)

        if plotly:
            # Edges
            edge_x, edge_y = map(lambda xs: intersperse_val(xs, None, 2, append = True), zip(*flatten([(coords[a], coords[b]) for a, b in self.G.edges()])))
            traces = [go.Scatter(x = edge_x, y = edge_y, showlegend = False,
                line = dict(width = 0.5, color = '#606060'), hoverinfo = 'none', mode = 'lines')]

            # Nodes by type
            for node_type, nodes in self.nodes_of_types().items():
                node_x, node_y = map(list, zip(*[coords[n] for n in nodes]))
                traces.append(go.Scatter(x = node_x, y = node_y,
                    name = node_type, mode = 'markers', hoverinfo = 'text', showlegend = True, # labels are annotations later, so no '+text' in mode
                    text = nodes, textposition = 'bottom center', # textfont = dict(size = 12, color = 'black'),
                    #legendgroup = 'Node Types', legendgrouptitle_text = 'Node Types',
                    marker = dict(showscale = False, size = 17, color = (col := mcolors.XKCD_COLORS[self.colour_map[node_type]]),
                                  line = dict(color = col, width = 2)) ))

            # Nodes in State
            node_x, node_y = map(list, zip(*[coords[n] for n in nodes_with_outline]))
            traces.append(go.Scatter(x = node_x, y = node_y,
                name = 'Node in State', mode = 'markers', showlegend = True,
                #legendgroup = 'State', legendgrouptitle_text = 'State',
                marker = dict(showscale = False, size = 17, color = 'rgba(0,0,0,0)',
                              line = dict(color = 'black', width = 3)) ))

            # All together
            fig = go.Figure(data = traces, layout = go.Layout(
                # title = 'GSM', titlefont_size = 16,
                showlegend = True, legend_title_text = 'Node Types',
                hovermode = 'closest',
                margin = dict(b = 20, l = 5, r = 5, t = 40),
                xaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
                yaxis = dict(showgrid = False, zeroline = False, showticklabels = False) ))

            # Labels (separate and as annotations in order to, respectively, write over nodes and control the angle)
            if radial_labels:
                for node in self.G.nodes:
                    fig.add_annotation(x = coords[node][0], y = coords[node][1], showarrow = False,
                        text = node, font = dict(size = 12, color = 'black'),
                        textangle = 180 - angle if abs(angle := radial_degrees(*coords[node])) > 90 else -angle,
                        xshift = (radial_offset := 17 + 3 * len(node)) * np.cos(rads := angle * np.pi / 180), yshift = radial_offset * np.sin(rads))
            else:
                for node in self.G.nodes:
                    fig.add_annotation(x = coords[node][0], y = coords[node][1], showarrow = False,
                        text = node, font = dict(size = 12, color = 'black'), yshift = -17)

            # Centre legend (only useful for shell layout)
            # fig.update_layout(legend = dict(x = 0.45, y = 0.55, bgcolor = 'rgba(0,0,0,0)'))

            fig.show()
            return fig
        else:
            node_cols, node_out_cols = self.get_node_colours(nodes_with_outline)
            # nx.draw also takes the arguments of nx.draw_networkx
            plot_args = dict(arrows = True, with_labels = True,
                node_color = node_cols, edgecolors = node_out_cols, linewidths = 3,
                font_size = 10, node_size = 500, edge_color = (0.2, 0.2, 0.2, 0.7))
            plot_args = {k: networkx_plot_args[k] if k in networkx_plot_args else v for k, v in plot_args.items()}
            nx.draw(self.G, coords, **plot_args)
            # The following is a networkx-matplotlib hack to print a colour legend: use empty scatter plots
            for t, c in self.colour_map.items(): plt.scatter([], [], c = [c], label = t)
            plt.legend()
            plt.show()
            return plt


