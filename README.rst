Graph-State-Machine
===================

.. image:: https://img.shields.io/pypi/v/Graph-State-Machine.svg
    :target: https://pypi.python.org/pypi/Graph-State-Machine/
    :alt: Latest PyPI version

.. image:: https://pepy.tech/badge/Graph-State-Machine
    :target: https://pepy.tech/project/Graph-State-Machine
    :alt: Package Downloads

.. image:: https://img.shields.io/pypi/pyversions/Graph-State-Machine.svg
    :target: https://pypi.python.org/pypi/Graph-State-Machine/
    :alt: Python Versions

.. image:: https://github.com/T-Flet/Graph-State-Machine/workflows/Python%20package/badge.svg
    :target: https://github.com/T-Flet/Graph-State-Machine/actions?query=workflow%3A%22Python+package%22
    :alt: Build

.. image:: https://img.shields.io/pypi/l/Graph-State-Machine.svg
    :target: https://github.com/T-Flet/Graph-State-Machine/blob/master/LICENSE
    :alt: License

A simple library to build easily interpretable computational constructs similar to Turing machines
over graphs, where states are combinations of a graph's (typed) nodes;
an example use would be a transparent backend logic which navigates an ontology


Installation
------------

::

    pip install Graph_State_Machine



Description
-----------

This package implements a computational construct similar to a Turing machine over a graph,
where states are node combinations (though more information may be stored) and where the arbitrary
transition function can update both state and graph.
Note that this last arbitrariness makes the system Turing complete since it allows implementing
a Turing machine with it (achieved by defining the graph to be a linear array and the state as a tuple
of node name and "head" state).

Given a graph with typed nodes and a state object from which a list of nodes can be extracted
(by an optional :code:`Selector` function), the construct applies two arbitrary functions to perform a step:

:code:`Scanner`
  A generalised neighbourhood function, which scans the graph "around" the state nodes,
  optionally by type, and returns a scored list of nodes for further processing
:code:`Step`
  A function to process the scan result and thus update the state and possibly the graph itself

(Note: the node ordering produced by a Scanner is unlikely to produce ties given the intentional
parsimony of options for each decision stage, but should one occur, as an artefact of the generalised
node neighbourhood process, the closest option to the earliest added state node will be selected first)

This computational construct is different from a finite state machine on a graph and from a
graph cellular automaton, but it shares some similarities with both in that it generalises some of
their features for the benefit of human ease of design and readability.
For example, a :code:`GSM`’s graph
generalises a finite state machine’s state graph by allowing the combinations of nodes to represent
state, and the scanner function is just a generalisation of a graph cellular automaton’s neighbourhood
function in both domain and codomain.
As previously mentioned, it is closer to a Turing machine on
a graph than either of the above, one whose programming is split between the internal state rules
and the graph topology, thus allowing programs to be simpler and with a more easily readable state.

Besides pure academic exploration of the construct, some possible uses of it are:

- implementing backend logics which are best represented by graphs, e.g. an "expert system"
- pathing through ontologies by entity proximity or similarity



Design
------

(Inspecting the package __init__.py imports is a quick and useful exercise in understanding the overall structure, while the following is a less concise version of the content of types.py)

Formalising the above description using library terminology, the constructor of the main class
(:code:`GSM`) takes the following arguments:

:code:`Graph`
  A graph object with typed nodes (wrapping a NetworkX graph),
  with utility methods so that it can be built from shorthand
  notation (structured edge lists), check its own consistency, self-display and extend itself by
  joining up with another with common nodes (exact ontology matching)
:code:`State`
  The initial state; the default type is a simple list of nodes (strings), but it can be anything as
  long as the used :code:`Scanner` function is designed to handle it and a function to extract a list of
  strings from it is provided as the Selector argument
:code:`Scanner` (:code:`Graph -> List[Node] -> Optional[NodeType] -> List[Tuple[Node, Any]]`)
  A function taking in a list of state nodes to use to determine next-step candidates, optionally focussing only
  on a specific node type
:code:`Updater` (:code:`State -> Graph -> ScanResult -> Tuple[State, Graph]`)
  A function taking in the current
  state and graph along with the result of a node scan and returns the updated state and graph
:code:`Selector` (:code:`State -> List[Node]`)
  A function to extract from the state the list of nodes which should
  be fed to the Scanner

A simple example of node-list state with non-identity Selector is a :code:`GSM` which only takes the last
"visited" node into account, and going one step further, an intuitive example of :code:`State` which is not
a simple node-list is a dictionary of node-lists only some subsets of which are considered for graph
exploration (and others for state updating), e.g. keeping track of which nodes were initial state and
which ones were added by steps.

Simple default constructor functions for this :code:`State` type are provided:
:code:`dict_fields_getter` (for :code:`selector`), which takes in the list of fields to concatenate, and :code:`list_in_dict_accumulator` (for :code:`Updater`), which takes in the single field to update.

Note: since the underlying object is a NetworkX graph, arbitrary node and edge attributes can be used to enhance the processing functions.



Simple Example
--------------

A GSM which determines the appropriate R linear regression function and distribution family from labelled data features:

- Define a numerical data-type ontology graph in the typed edge-list shorthand which :code:`Graph` accepts along with ready-made Networkx graphs, making use of two simple notation helper functions
- Create a default-settings :code:`GSM` with it and a simple starting state
- Ask it to perform steps focussing on the node types of 'Distribution', 'Method Function' and 'Family Implementation', which in this context just means finding the most appropriate of each

.. figure:: showcase_graph.png
    :align: center
    :figclass: align-center

.. code-block:: Python

    from Graph_State_Machine import *

    _shorthand_graph = {
        'Distribution': {
            'Normal': ['stan_glm', 'glm', 'gaussian'],
            'Binomial': ['stan_glm', 'glm', 'binomial'],
            'Multinomial': ['stan_polr', 'polr'],
            'Poisson': ['stan_glm', 'glm', 'poisson'],
            'Beta': ['stan_betareg', 'betareg'],
            'Gamma D': ['stan_glm', 'glm', 'Gamma'],
            'Inverse Gaussian': ['stan_glm', 'glm', 'inverse.gaussian']
        },
        'Family Implementation': strs_as_keys(['binomial', 'poisson', 'Gamma', 'gaussian', 'inverse.gaussian']),
        'Method Function': strs_as_keys(['glm', 'betareg', 'polr', 'stan_glm', 'stan_betareg', 'stan_polr']),
        'Data Feature': adjacencies_lossy_reverse({ # Reverse-direction definition here since more readable i.e. defining the contents of the lists
            'Binomial': ['Binary', 'Integer', '[0,1]', 'Boolean'],
            'Poisson': ['Non-Negative', 'Integer', 'Non-Zero'],
            'Multinomial': ['Factor', 'Consecutive', 'Non-Negative', 'Integer'],
            'Normal': ['Integer', 'Real'],
            'Beta': ['Real', '[0,1]'],
            'Gamma D': ['Non-Negative', 'Real', 'Non-Zero']
        })
    }

    gsm = GSM(Graph(_shorthand_graph), ['Non-Negative', 'Non-Zero', 'Integer']) # Default function-arguments

    gsm.plot()

    gsm.consecutive_steps(['Distribution', 'Family Implementation']) # Perform 2 steps
    # gsm.parallel_steps(['Distribution', 'Family Implementation']) # Warn of failure for 'Family Implementation' if parallel
    print(gsm._scan('Method Function')) # Peek at intermediate value of new a step
    gsm.step('Method Function') # Perform the step
    gsm.step('NON EXISTING TYPE') # Trigger a warning and no State changes

    print(gsm)


The 'Method Function' scan above is peeked at before its step to show that there is a tie between a Frequentist and a Bayesian method.
This is a trivial example (in that the simple addition could have been there from the beginning) of where a broader graph could be attached by :code:`gsm.extend_with(...)` and new state introduced in order to resolve the tie.

Note that ties need not really be resolved as long as the :code:`Updater` function's behaviour is what the user expects since it is not limited in functionality; it could select a random option, all, some or none of them, it could adjust the graph itself or terminate execution.


