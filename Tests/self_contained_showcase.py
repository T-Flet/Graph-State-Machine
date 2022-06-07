import networkx as nx

from Graph_State_Machine import *

_shorthand_graph = {
    'Distribution': {
        'Normal': dict(necessary_for = ['gaussian'], plain = ['stan_glm', 'glm']),
        'Binomial': dict(necessary_for = ['binomial'], plain = ['stan_glm', 'glm']),
        'Multinomial': dict(necessary_for = ['multinom'], plain = ['stan_polr', 'polr_tolerant']),
        'Poisson': dict(necessary_for = ['poisson'], plain = ['stan_glm', 'glm']),
        'Beta': dict(necessary_for = ['betareg'], plain = ['stan_betareg']),
        'gamma': dict(necessary_for = ['Gamma'], plain = ['stan_glm', 'glm']),
        'Inverse Gaussian': dict(necessary_for = ['inverse.gaussian'], plain = ['stan_glm', 'glm']),
    }, # The end-nodes of the edges above need to be declared as of some type (below), but no need to repeat or split the edges
    'Family Implementation': strs_as_keys(['binomial', 'poisson', 'Gamma', 'gaussian', 'inverse.gaussian']),
    'Methodology Function': strs_as_keys(['glm', 'betareg', 'polr_tolerant', 'multinom', 'stan_glm', 'stan_betareg', 'stan_polr']),
    'Data Feature': reverse_adjacencies({ # Reverse-direction definition here since more readable i.e. defining the contents of the lists
        'Binomial': dict(are_sufficient = ['Binary', 'Boolean'], plain = ['Integer', '[0,1]']),
        'Poisson': dict(are_necessary = ['Counts-Like', 'Non-Negative', 'Integer'], plain = ['Consecutive']),
        'Multinomial': dict(are_sufficient = ['Factor'], plain = ['Consecutive', 'Non-Negative', 'Integer']),
        'Normal': ['Integer', 'Real', '+ and -'],
        'Beta': dict(are_necessary = ['Real', '[0,1]']),
        'gamma': dict(are_necessary = ['Non-Negative', 'Non-Zero'], plain = ['Integer', 'Real']),
        'Inverse Gaussian': dict(are_necessary = ['Non-Negative', 'Non-Zero'], plain = ['Integer', 'Real']),
        'polr_tolerant': ['Consecutive']
    })
}

gsm = GSM(Graph(_shorthand_graph), ['Non-Negative', 'Non-Zero', 'Integer']) # Using default arguments
    # The default node_scanner is by jaccard similarity score, and supports 4 additional arguments to filter candidates
    # and their neighbours by type; only the first one (candidate type list) is used in the examples below

# gsm.plot()
# gsm.plot(layout = nx.shell_layout, radial_labels = True)
# gsm.plot(plotly = False)

gsm.consecutive_steps(dict(candidate_types = ['Distribution']), dict(candidate_types = ['Family Implementation']))
    # Perform 2 steps, giving one optional argument (incidentally, the first one) for each step,
    # i.e. the (singleton) list of types to focus on

# gsm.consecutive_steps([['Distribution']], [['Family Implementation']]) # Unnamed-arguments version of the above
# gsm.parallel_steps([['Distribution']], [['Family Implementation']]) # Parallel version, warning of failure for 'Family Implementation'
print(gsm.log[-2], '\n') # Can check the log for details of the second-last step, where a tie occurs.
                         # Ties are rare, and the default Updater only picks one result, but arbitrary action may be taken

print(gsm._scan(['Methodology Function']), '\n') # Can also peek ahead at the intermediate value of a possible next step
gsm.step(['Methodology Function']) # Perform the step

gsm.step(['NON EXISTING TYPE']) # Trigger a warning and no State changes
print(gsm.log[-1], '\n') # The failed step is also logged

print(gsm)