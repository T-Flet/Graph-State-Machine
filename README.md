# Graph-State-Machine
A simple framework for building FSMs where states are combinations of a graph's (typed) nodes; an example use would be as intuitive back-end logic by pathing through an ontology.


A simple framework to step through a graph given a state by identifying best-matching 'next' nodes.

- Provides "state" and "ontology" constructs 
    - State: string list or at most string-scores/weights dictionary
    - Ontology: graph with string nodes with types, capable of:
        - Self-build from shorthand notation (structured edge lists)
        - Check consistency (to be defined)
        - Self-display
        - Join up with another with common nodes (exact ontology matching)
- Allow definition and application of "reasoning" rules of this form:
    - Given a state, an ontology and arbitrary restrictions (weight/scores, range, types)
    - Return ordered "matches" (nodes) from the ontology to the state


