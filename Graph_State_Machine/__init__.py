"""Graph-State-Machine - A simple framework for building easily interpretable computational constructs between a graph automaton and a Turing machine where states are combinations of a graph's (typed) nodes; an example use would be as transparent backend logic by pathing through an ontology"""

__version__ = '0.4.1' # Update in setup.py too
__author__ = 'Thomas Fletcher <T-Fletcher@outlook.com>'
# __all__ = ['Graph', 'GSM']


# Core imports
from Graph_State_Machine.graph import Graph
from Graph_State_Machine.gsm import GSM

# Graph-construction utility functions
from Graph_State_Machine.Util.misc import strs_as_keys, adjacencies_lossy_reverse

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


