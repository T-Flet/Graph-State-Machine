import networkx as nx
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from copy import deepcopy
from warnings import warn

from Graph_State_Machine.Util.generic_util import diff, group_by, flatten, intersperse_val
from Graph_State_Machine.Util.misc import check_edge_dict_keys, radial_degrees

from typing import *
Node = str
NodeType = str
TypedAdjacencies = Dict[NodeType, Dict[Node, Union[List[Node], Dict[str, List[Node]]]]]



class Graph:
    def __init__(self, G: Union[nx.Graph, TypedAdjacencies], type_attr: NodeType = 'node_type', warn_about_problematic_sufficiencies = True):
        '''Note: the constructor accepts either a Networkx Graph or a Dict[NodeType, Dict[Node, List[Node]]] (aliased to TypedAdjacencies internally).
        Calling the constructor with the latter is equivalent to Graph(Graph.read_typed_adjacency_list(TypedAdjacencies_OBJECT, type_attr), type_attr)'''
        self.type_attr = type_attr
        self.default_cols = None
        self.colour_map = None

        if not isinstance(G, nx.Graph): G = Graph.read_typed_adjacency_list(G, self.type_attr)
        self._set_graph(G, warn_about_problematic_sufficiencies)


    # Init-related methods

    def _set_graph(self, G: nx.Graph, warn_about_problematic_sufficiencies = True):
        self.G = G
        self.consistent(warn_about_problematic_sufficiencies)

        self.nodes_to_types = self._get_nodes_to_types()
        self.types = sorted(list(set(nx.get_node_attributes(self.G, self.type_attr).values())))

        self._set_colours()
        return self

    @staticmethod
    def read_typed_adjacency_list(tas: TypedAdjacencies, type_attr: NodeType = 'node_type') -> nx.Graph:
        G = nx.Graph()
        for nt, one_to_many in tas.items(): G.add_nodes_from(one_to_many.keys(), **{type_attr: nt}) # Separate loop because nodes need to exist before edges
        for nt, one_to_many in tas.items(): # G.add_edges_from([(start, end) for start, many in one_to_many.items() for end in many])
            for start, many in one_to_many.items():
                # This is fine without edge existence checks because re-adding an edge with or without attributes only updates it constructively
                if isinstance(many, list): G.add_edges_from([(start, end) for end in many])
                else: # isinstance(one_to_many, dict)
                    check_edge_dict_keys(many)
                    G.add_edges_from([(start, end) for end in flatten(many.values())])
                    # No need to do anything with the 'plain' list below since its edges are already added above
                    Graph._parse_edge_attributes(G, start, many, 'are_necessary', 'necessary_for', False)
                    Graph._parse_edge_attributes(G, start, many, 'are_sufficient', 'sufficient_for', False)
                    Graph._parse_edge_attributes(G, start, many, 'necessary_for', 'necessary_for', True)
                    Graph._parse_edge_attributes(G, start, many, 'sufficient_for', 'sufficient_for', True)
        return G

    @staticmethod
    def _parse_edge_attributes(G: nx.Graph, start: Node, many_dict: Dict[str, List[Node]], list_name: str, attribute_name: str, set_to_end = False) -> None:
        '''Takes in a graph, a start node, a dictionary of lists of end nodes, the key of one of the lists, the name of an edge attribute
            and whether said attribute should be set to the start or end node. Returns nothing; modifies input G'''
        if list_name in many_dict:
            for end in many_dict[list_name]:
                set_to = end if set_to_end else start
                if (nfor := G[start][end].get(attribute_name)):
                    if set_to == nfor: warn(f"Redundancy in typed adjacency list: the '{attribute_name}' attribute of edge '{start}'-'{end}' was already set")
                    else: raise ValueError(  f"Conflict in typed adjacency list: the '{attribute_name}' attribute of edge '{start}'-'{end}' was already set")
                G.add_edge(start, end, **{attribute_name: set_to}) # Reached if no error was raised

    def consistent(self, warn_about_problematic_sufficiencies = True):
        typed_ns = set(nx.get_node_attributes(self.G, self.type_attr).keys())
        assert set(self.G.nodes) == typed_ns, f'Some nodes have no type: {set(self.G.nodes) - typed_ns}'
        if warn_about_problematic_sufficiencies: self._check_problematic_sufficiencies()
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

    def group_nodes(self, nodes: List[Node] = None) -> Dict[NodeType, List[Node]]:
        unsorted = group_by(lambda n: self.nodes_to_types[n], nodes if nodes else self.G.nodes())
        return {nt: unsorted[nt] for nt in sorted(unsorted)}

    def extend_with(self, extension_graph):
        '''Note: returns a new object; does not affect the original'''
        res = deepcopy(self)
        return res._set_graph(nx.compose(res.G, extension_graph.G))


    # Utility methods

    def relevant_neighbours(self, nodes: List[Node], good_types: List[NodeType] = None, bad_types: List[NodeType] = None) -> List[List[Node]]:
        '''Return neighbours of state nodes of the specified types or all types if none specified'''
        return [self.type_filter(self.G.neighbors(sn), good_types, bad_types) for sn in nodes]

    def type_filter(self, nodes: List[Node] = None, good_types: List[NodeType] = None, bad_types: List[NodeType] = None) -> List[Node]:
        '''Keep nodes of good_types and discard those of bad_types'''
        good_types = set(good_types if good_types else self.types).difference(bad_types if bad_types else [])
        return [n for n in (nodes if nodes else self.G.nodes) if self.G.nodes[n][self.type_attr] in good_types]

    def necessity_sufficiency_filter(self, list_state: List[Node], candidates: List[Node], check_only_state_types = False) -> List[Node]:
        '''Keep candidates who have all their necessary neighbours and any of their sufficient ones in list_state
            Setting count_only_state_types to True restricts necessity/sufficiency checks to only nodes of types present in the state;
                this is reasonable for GSMs performing some sequential pathing through an ontology,
                in which nodes of types not yet in consideration should not affect steps before they are'''
        state_types = set(self.nodes_to_types[c] for c in candidates)
        return [c for c in candidates
                if (edges := self.G.edges(c, data = True), # Assignments in a single tuple so that it evaluates to True
                    necessary  := [n for _, n, d in edges if d.get('necessary_for')  == c],
                    sufficient := [n for _, n, d in edges if d.get('sufficient_for') == c])
                if not necessary or all(n in list_state or (check_only_state_types and self.nodes_to_types[n] not in state_types) for n in necessary)
                if not sufficient or any(s in list_state or (check_only_state_types and self.nodes_to_types[n] not in state_types) for s in sufficient)]

    def _check_problematic_sufficiencies(self):
        if problematic := {c: dict(are_sufficient = sufficient, plain = plain) for c in self.G.nodes
         if (edges := self.G.edges(c, data = True), # Assignments in a single tuple so that it evaluates to True
             sufficient := [n for _, n, d in edges if d.get('sufficient_for') == c],
             plain      := [n for _, n, d in edges if d.get('sufficient_for') == d.get('necessary_for') == None])
         if sufficient and plain}:
            warn(f'IMPORTANT:\n'
                 f'Some nodes in the graph (reported below) have both some neighbours which are sufficient for them and some with plain edges.\n'
                 f'If this is not intentional, be aware that strictly checking for sufficiency may lead to situations in which these nodes '
                 f'will be discarded if no sufficient neighbour is in state EVEN if all plain ones are (which would be problematic if, say, '
                 f'those plain ones were jointly sufficient).\n\n'
                 f'The problematic nodes are: {problematic}\n\n'
                 f'Possible solutions to this situation include:\n '
                 f'\t- carefully checking that this is not a problem for the given use case\n'
                 f'\t- carefully checking that changing some Scanner parameter (possibly check_only_state_types) ensure this is not a problem for the given use case\n'
                 f'\t- redesigning the involved graph portions to interpose a new node type such that all '
                 f'its instances are on one side sufficient for the node in question and on the other are reached by jointly-sufficient current '
                 f'neighbour collections\n'
                 f'\t- using necessity but not sufficiency (i.e. removing the sufficiency edge attributes)\n\n'
                 f'Ideally the situation would be resolved by addressing the cause of this warning, but if it is acceptably handled by determining '
                 f'things are fine as they are, this warning may be suppressed by setting warn_about_problematic_sufficiencies to False on Graph declaration '
                 f'(and, if desired, on independent calls to the .consistent method).')


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
            # All edges
            edge_x, edge_y = map(lambda xs: intersperse_val(xs, None, 2, append = True), zip(*flatten([(coords[a], coords[b]) for a, b in self.G.edges()])))
            traces = [go.Scatter(x = edge_x, y = edge_y, showlegend = False,
                line = dict(width = 0.5, color = '#606060'), hoverinfo = 'none', mode = 'lines')]

            # Necessity & sufficiency arrows (added to fig itself later, but prepared here for tidiness)
            digraphs = dict(necessary_for = [], sufficient_for = [])
            for a, b, d in self.G.edges(data = True):
                for attr in d: digraphs[attr].append((a, b)[::(-1 if d[attr] == a else 1)])
            arrows = []
            for attr, colour, width, shorter in [('necessary_for', 'tomato', 2.5, 0.02), ('sufficient_for', 'royalblue', 1.5, 0.01)]:
                for a, b in digraphs[attr]:
                    ax, ay, bx, by = coords[a][0], coords[a][1], coords[b][0], coords[b][1]
                    # Would use the below arrow shortening in order not to cross nodes' boundaries, but plotly scales the coordinates
                    #   to match the window shape, therefore any in-coordinates shift becomes disproportionate;
                    #   would need absolute coordinates (like those determining the node size from a parameter)
                    # angle = np.arctan2([by - ay], [bx - ax])[0]
                    # ax += shorter * np.cos(angle)
                    # bx -= shorter * np.cos(angle)
                    # ay += shorter * np.sin(angle)
                    # by -= shorter * np.sin(angle)
                    arrows.append(go.layout.Annotation(dict(
                        x = bx, y = by, ax = ax, ay = ay,
                        xref = 'x', yref = 'y', axref = 'x', ayref = 'y', text = '',
                        showarrow = True, arrowhead = 3, arrowwidth = width, arrowsize = 1, arrowcolor = colour) ) )

            # Nodes by type
            for node_type, nodes in self.group_nodes().items():
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
                margin = dict(t = 25, b = 20, l = 5, r = 5),
                xaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
                yaxis = dict(showgrid = False, zeroline = False, showticklabels = False) ))
            fig.update_layout(annotations = arrows) # Necessity & sufficiency

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

            # Necessity & sufficiency arrows
            digraphs = dict(necessary_for = [], sufficient_for = [])
            for a, b, d in self.G.edges(data = True):
                for attr in d: digraphs[attr].append((a, b)[::(-1 if d[attr] == a else 1)])
            for attr, colour, width, arrowsize in [('necessary_for', 'tomato', 2, 25), ('sufficient_for', 'royalblue', 1, 20)]:
                nx.draw_networkx_edges(nx.DiGraph(digraphs[attr]), coords,#{k: v for k, v in coords.items() if k in dg.nodes()},
                   edge_color = colour, arrows = True, width = width, arrowsize = arrowsize, arrowstyle = '-|>') # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.ArrowStyle.html#matplotlib.patches.ArrowStyle

            # The following is a networkx-matplotlib hack to print a colour legend: use empty scatter plots
            for t, c in self.colour_map.items(): plt.scatter([], [], c = [c], label = t)
            plt.legend()
            plt.show()
            return plt


