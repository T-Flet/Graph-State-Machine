from Graph_State_Machine import *

_shorthand_graph = {
    'Distribution': {
        'Normal': ['stan_glm', 'glm', 'gaussian'],
        'Binomial': ['stan_glm', 'glm', 'binomial'],
        'Categorical': ['stan_polr', 'polr_tolerant', 'multinom'],
        'Poisson': ['stan_glm', 'glm', 'poisson'],
        'Beta': ['stan_betareg', 'betareg'],
        'Gamma_': ['stan_glm', 'glm', 'Gamma'],
        'Inverse Gaussian': ['stan_glm', 'glm', 'inverse.gaussian']
    },
    'Family Implementation': strs_as_keys(['binomial', 'poisson', 'Gamma', 'gaussian', 'inverse.gaussian']),
    'Methodology Function': strs_as_keys(['glm', 'betareg', 'polr_tolerant', 'multinom', 'stan_glm', 'stan_betareg', 'stan_polr']),
    'Data Feature': reverse_adjacencies({ # Reverse-direction definition here since more readable i.e. defining the contents of the lists
        'Binomial': ['Binary', 'Integer', '[0,1]', 'Boolean'],
        'Poisson': ['Non-Negative', 'Integer', 'Consecutive', 'Counts-Like'],
        'Categorical': ['Factor', 'Consecutive', 'Non-Negative', 'Integer'],
        'Normal': ['Integer', 'Real', '+ and -'],
        'Beta': ['Real', '[0,1]'],
        'Gamma_': ['Non-Negative', 'Integer', 'Real', 'Non-Zero'],
        'Inverse Gaussian': ['Non-Negative', 'Integer', 'Real', 'Non-Zero'],
        'polr_tolerant': ['Consecutive']
    })
}

gsm = GSM(Graph(_shorthand_graph), ['Non-Negative', 'Non-Zero', 'Integer']) # Using default arguments
    # The default node_scanner is by jaccard similarity score, and takes additional arguments to filter candidates
    # and their neighbours by type; only the first one (candidate type list) is used in the examples below

# gsm.plot()
# import networkx as nx
# gsm.plot(layout = nx.shell_layout, radial_labels = True) # Some other layout
# gsm.plot(plotly = False, show_necessity = False, show_sufficiency = True) # Networkx's native plotting backend instead of Plotly

gsm.consecutive_steps(dict(candidate_types = ['Distribution']), dict(candidate_types = ['Family Implementation']))
    # Perform 2 steps, providing named arguments (in this case only one) to the Scanner function as a dictionary

# gsm.consecutive_steps([['Distribution']], [['Family Implementation']]) # Unnamed-arguments version of the above
# gsm.parallel_steps([['Distribution']], [['Family Implementation']]) # Parallel version, warning of failure for 'Family Implementation'

print(gsm.log[-2], '\n') # Can check the log for details of the second-last step, where a tie occurs.
                         # Ties are rare, and the default Updater only picks one result, but arbitrary action may be taken

print(gsm._scan(['Methodology Function']), '\n') # Can also peek at the intermediate value of a step without going through with it
gsm.step(['Methodology Function']) # Perform the step (unnamed-Scanner-arguments version)

gsm.step(['NON EXISTING TYPE']) # Trigger a warning and no State changes
print(gsm.log[-1], '\n') # The failed step is also logged

print(gsm) # Prints the GSM State


