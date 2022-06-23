import networkx as nx
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pprint import pformat
from copy import deepcopy
from warnings import warn

from Graph_State_Machine.Util.generic_util import diff, group_by, flatten, intersperse_val
from Graph_State_Machine.Util.misc import check_edge_dict_keys, radial_degrees

from typing import *
Node = str
NodeType = str
TypedAdjacencies = Dict[NodeType, Dict[Node, Union[List[Node], Dict[str, List[Union[Node, List[Node]]]]]]]



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
        assert all(isinstance(nt, NodeType) for nt in tas.keys())
        assert all(isinstance(n, Node) for nt in tas.keys() for n in tas[nt].keys())

        G = nx.Graph()
        for nt, one_to_many in tas.items(): G.add_nodes_from(one_to_many.keys(), **{type_attr: nt}) # Separate loop because nodes need to exist before edges
        for nt, one_to_many in tas.items(): # G.add_edges_from([(start, end) for start, many in one_to_many.items() for end in many])
            for start, many in one_to_many.items():
                # This is fine without edge existence checks because re-adding an edge with or without attributes only updates it constructively
                if isinstance(many, list): G.add_edges_from([(start, end) for end in many])
                else: # isinstance(one_to_many, dict)
                    check_edge_dict_keys(many)
                    G.add_edges_from([(start, end) for end in flatten([n_or_ns if isinstance(n_or_ns, list) else [n_or_ns] for n_or_ns in flatten(many.values())])])
                    # No need to do anything with the 'plain' list below since its edges are already added above
                    Graph._parse_necessity_sufficiency(G, start, many, 'are_necessary', 'necessary', False)
                    Graph._parse_necessity_sufficiency(G, start, many, 'are_sufficient', 'sufficient', False)
                    Graph._parse_necessity_sufficiency(G, start, many, 'necessary_for', 'necessary', True)
                    Graph._parse_necessity_sufficiency(G, start, many, 'sufficient_for', 'sufficient', True)
        return G

    @staticmethod
    def _parse_necessity_sufficiency(G: nx.Graph, start: Node, many_dict: Dict[str, List[Node]], list_name: str, attribute_name: str, set_end_side = False, allow_symmetric_necessity = False) -> None:
        '''Takes in a graph, a start node, a dictionary of lists of end nodes, the key of one of the relationship dictionary lists,
            the name of a node attribute and whether it should be of the start node or end node. Returns nothing; modifies input G.
            This function assumes list_name and attribute name have been deemd acceptable.
            NOTE: do not set set_end_side to True if list_name is 'are_sufficient' and there are lists intermixed with its content
                because this function will place the list values (as sets) in the start node's attribute_name
                and the string values to the end note's'''
        if list_name in many_dict:
            for end in many_dict[list_name]:
                if isinstance(end, list):
                    if list_name != 'are_sufficient': raise ValueError(f"All adjacency keys except 'are_sufficient' need to be simple lists of Nodes; instead '{list_name}' contained a list: {end}")
                    side_to_set, value = start, set(end)
                else:
                    side_to_set, value = (start, end)[::(-1 if set_end_side else 1)]
                    if value == side_to_set:
                        warn(f"Ignored attempt to append node '{value}' to its own '{attribute_name}' attribute")
                        continue

                if list_name in ['are_necessary', 'necessary_for'] and attribute_name in G.nodes[value] and side_to_set in G.nodes[value][attribute_name]:
                    if allow_symmetric_necessity: warn(f"Allowing attempt to have nodes '{side_to_set}' and '{value}' have each other in their '{attribute_name}' attribute, which would make them unreachable by any step function making sensible use of this information; set allow_symmetric_necessity to False to turn this into an error")
                    else: raise ValueError(             f"Stopped attempt to have nodes '{side_to_set}' and '{value}' have each other in their '{attribute_name}' attribute, which would make them unreachable by any step function making sensible use of this information; set allow_symmetric_necessity to True to turn this into a warning")
                elif list_name in ['are_sufficient', 'sufficient_for'] and not isinstance(value, set): value = set([value]) # Make singletons for consistency

                if attribute_name in G.nodes[side_to_set]:
                    if value in G.nodes[side_to_set][attribute_name]: warn(f"Redundancy in typed adjacency list: the '{attribute_name}' attribute of node '{side_to_set}' already contained {value}")
                    else: G.nodes[side_to_set][attribute_name].append(value)
                else: G.nodes[side_to_set][attribute_name] = [value]

    def consistent(self, warn_about_problematic_sufficiencies = True):
        '''This function does not check some obvious things which should come about automatically from read_typed_adjacency_list
        on Graph declaration but which could be ruined later by manually setting new node attributes.
        (Things like all nodes in necessity/sufficiency attributes actually having an edge to the given node
        or node pairs not having each other in the necessary attribute,
        which would make them unreachable by any step function making sensible use of this information but could be allowed by setting
        read_typed_adjacency_list's allow_symmetric_necessity argument to True)'''
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

    def type_set(self, nodes: List[Node]) -> Set[NodeType]: return set(self.nodes_to_types[n] for n in nodes)

    def relevant_neighbours(self, nodes: List[Node], good_types: List[NodeType] = None, bad_types: List[NodeType] = None) -> List[List[Node]]:
        '''Return neighbours of state nodes of the specified types or all types if none specified'''
        return [self.type_filter(self.G.neighbors(sn), good_types, bad_types) for sn in nodes]

    def type_filter(self, nodes: List[Node] = None, good_types: List[NodeType] = None, bad_types: List[NodeType] = None) -> List[Node]:
        '''Keep nodes of good_types and discard those of bad_types'''
        good_types = set(good_types if good_types else self.types).difference(bad_types if bad_types else [])
        return [n for n in (nodes if nodes else self.G.nodes) if self.G.nodes[n][self.type_attr] in good_types]

    def necessity_sufficiency_filter(self, list_state: List[Node], candidates: List[Node],
                                     check_necessity = True, check_sufficiency = True,
                                     check_only_state_types = False) -> List[Node]:
        '''Keep candidates who have all their necessary neighbours and any of their sufficient ones in list_state
            Setting check_only_state_types to True restricts necessity/sufficiency checks to only nodes of types present in the state;
                this is reasonable for GSMs performing some sequential pathing through an ontology,
                in which nodes of types not yet in consideration should not affect steps before they are'''
        if not check_necessity and not check_sufficiency:
            warn('Called necessity_sufficiency_filter with both check_necessity and check_sufficiency False; candidates passed through unaffected')
            return candidates

        state_types = self.type_set(list_state) # Otherwise recomputed for every candidate
        return [c for c in candidates # Assignments in a single tuple below so that it evaluates to True
                if (necessary := self.G.nodes[c].get('necessary'), sufficient := self.G.nodes[c].get('sufficient'))
                if not check_necessity   or not necessary  or     all(n in list_state or (check_only_state_types and self.nodes_to_types[n] not in state_types) for n in necessary)
                if not check_sufficiency or not sufficient or any(all(n in list_state or (check_only_state_types and self.nodes_to_types[n] not in state_types) for n in ns) for ns in sufficient)]

    def plain_edges(self, n: Node) -> List[Node]:
        '''Returns the nodes with which the given node has edges carrying neither necessity nor sufficiency in either direction'''
        own_non_plain = set(self.G.nodes[n].get('necessary', [])).union(flatten(self.G.nodes[n].get('sufficient', [])))
        return [b for _, b in self.G.edges(n) if b not in own_non_plain
            if n not in set(self.G.nodes[b].get('necessary', [])).union(flatten(self.G.nodes[b].get('sufficient', [])))]

    def _check_problematic_sufficiencies(self):
        if problematic := {c: dict(are_sufficient = sufficient, plain = plain) for c in self.G.nodes
         if (sufficient := self.G.nodes[c].get('sufficient')) if (plain := self.plain_edges(c))}:
            warn(f'\n\nIMPORTANT:\n'
                 f'Some nodes in the graph (reported below) have both some neighbours which are sufficient for them and some with plain edges.\n'
                 f'If this is not intentional, be aware that strictly checking for sufficiency may lead to situations in which these nodes '
                 f'will be discarded if no sufficient set of neighbours is in state EVEN if all plain ones are.\n\n'
                 f'The perhaps problematic nodes are:\n{pformat(problematic)}\n\n'
                 f'Possible actions to take include:\n '
                 f'\t- carefully checking that the plain edges in the above are fine as they are (i.e. that they are not undeclared sufficient or jointly-sufficient ones) and correct them otherwise\n'
                 f'\t- carefully checking that this is not a problem for the given use case (perhaps by changing some Scanner parameter, e.g. check_only_state_types)\n'
                 f'Once things are deemed to be fine, this warning may be suppressed by setting warn_about_problematic_sufficiencies to False on Graph declaration '
                 f'(and, if desired, on independent calls to the .consistent method).\n')


    # Plotting methods

    def get_node_colours(self, nodes_with_outline = None) -> Tuple[List[str], List[str]]:
        cols = [self.colour_map[u[1]] for u in self.G.nodes(data = self.type_attr)] # Not pattern-matching the pair for consistency with u below
        if nodes_with_outline:
            outs = ['#606060' if u[0] in nodes_with_outline else c for u, c in zip(self.G.nodes(data = self.type_attr), cols)]
            return cols, outs
        else: return cols, cols

    def plot(self, nodes_with_outline: List[Node] = None,
             show_necessity = True, show_sufficiency = True,
             layout: Callable[[Any], Dict[Any, Iterable[float]]] = nx.kamada_kawai_layout, layout_args: Dict[str, Any] = {},
             plotly = True, radial_labels = False, networkx_plot_args: Dict[str, Any] = {}):
        '''Plots the GSM graph either through plotly or networkx.
            - layout and layout_args are always used
            - networkx_plot_args is only used if plotly is False; reference for its content: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html .
            - radial_labels is only used if plotly is True, and is intended for use with the nx.shell_layout layout'''
        coords = layout(self.G, **layout_args)
        digraphs = self._get_nec_suff_arrows()

        if plotly:
            # Necessity & sufficiency arrows (added to fig itself later, but prepared here for tidiness)
            arrows = []
            for attr, colour, width, shorter in [('necessary', 'tomato', 2.5, 0.02), ('sufficient', 'royalblue', 1.5, 0.01), ('jointly_sufficient', '#839deb', 1.5, 0.01)]:
                if not show_necessity   and attr == 'necessary':  continue
                if not show_sufficiency and attr == 'sufficient': continue
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

            # All edges
            edge_x, edge_y = map(lambda xs: intersperse_val(xs, None, 2, append = True), zip(*flatten([(coords[a], coords[b]) for a, b in self.G.edges()])))
            traces = [go.Scatter(x = edge_x, y = edge_y, showlegend = True, name = 'Plain Edges' if any(digraphs.values()) and (show_necessity or show_sufficiency) else 'Edges',
                line = dict(width = 0.5, color = '#606060'), hoverinfo = 'none', mode = 'lines')]

            # 0-length edges to generate legend entries for the necessity/sufficiency ones
            for attr, label, colour in [('necessary', 'Necessary', 'tomato'), ('sufficient', 'Sufficient', 'royalblue'), ('jointly_sufficient', 'Jointly Sufficient', '#839deb')]:
                if not digraphs[attr]: continue
                traces.append(go.Scatter(x = [0], y = [0], mode = 'lines', showlegend = True, name = label, marker = dict(color = colour)))

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
                showlegend = True, legend_title_text = 'Node Types & Edges',
                hovermode = 'closest',
                margin = dict(t = 25, b = 20, l = 5, r = 5),
                xaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
                yaxis = dict(showgrid = False, zeroline = False, showticklabels = False) ))
            fig.update_layout(annotations = arrows) # necessity & sufficiency if present

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
            for attr, colour, style, width, arrowsize in [('necessary', 'tomato', 'solid', 2, 25), ('sufficient', 'royalblue', 'solid', 1, 20), ('jointly_sufficient', '#839deb', 'solid', 1, 20)]:
                if not show_necessity   and attr == 'necessary':  continue
                if not show_sufficiency and attr == 'sufficient': continue
                nx.draw_networkx_edges(nx.DiGraph(digraphs[attr]), coords,# This restriction is redundant: {k: v for k, v in coords.items() if k in dg.nodes()},
                   edge_color = colour, arrows = True, width = width, style = style, arrowsize = arrowsize, arrowstyle = '-|>') # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.ArrowStyle.html#matplotlib.patches.ArrowStyle

            # The following is a networkx-matplotlib hack to print a colour legend: use empty scatter plots
            for t, c in self.colour_map.items(): plt.scatter([], [], c = [c], label = t)
            plt.legend()
            plt.show()
            return plt

    def _get_nec_suff_arrows(self):
        digraphs = dict(necessary = [], sufficient = [], jointly_sufficient = [])
        for b, d in self.G.nodes(data = True):
            if 'necessary' in d: digraphs['necessary'] += [(a, b) for a in d['necessary']]
            if 'sufficient' in d:
                for a_or_as in d['sufficient']:
                    if len(a_or_as) == 1: digraphs['sufficient'].append((list(a_or_as)[0], b))
                    else: digraphs['jointly_sufficient'] += [(a, b) for a in a_or_as]
        return digraphs


