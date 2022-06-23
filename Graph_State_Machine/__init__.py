"""Graph-State-Machine - A simple library to build easily interpretable computational constructs similar to a Turing machine over a graph, where states are combinations of a graph's (typed) nodes; an example use would be a transparent backend logic which navigates an ontology"""

__version__ = '3.1' # Change it in setup.py too
__author__ = 'Thomas Fletcher <T-Fletcher@outlook.com>'
# __all__ = ['Graph', 'GSM']


# Core imports
from Graph_State_Machine.graph import Graph
from Graph_State_Machine.gsm import GSM

# Graph-construction utility functions
from Graph_State_Machine.Util.misc import strs_as_keys, reverse_adjacencies

# Basic examples and constructors for each function group
from Graph_State_Machine.selectors import identity, last_only, dict_fields_getter
from Graph_State_Machine.scanners import by_score, neighbour_intersection
from Graph_State_Machine.scores import presence_score, jaccard_similarity
from Graph_State_Machine.updaters import list_accumulator, list_in_dict_accumulator

# Function groups named imports instead
# import Graph_State_Machine.selectors as sels
# import Graph_State_Machine.scanners as scans
# import Graph_State_Machine.scores as scores
# import Graph_State_Machine.updaters as ups


