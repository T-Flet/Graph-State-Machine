
from Graph_State_Machine import *

_shorthand_graph = {
    'Distribution': {
        'Normal': ['stan_glm', 'glm', 'gaussian'],
        'Binomial': ['stan_glm', 'glm', 'binomial'],
        'Multinomial': ['stan_polr', 'polr_tolerant', 'multinom'],
        'Poisson': ['stan_glm', 'glm', 'poisson'],
        'Beta': ['stan_betareg', 'betareg'],
        'gamma': ['stan_glm', 'glm', 'Gamma'],
        'Inverse Gaussian': ['stan_glm', 'glm', 'inverse.gaussian']
    },
    'Family Implementation': strs_as_keys(['binomial', 'poisson', 'Gamma', 'gaussian', 'inverse.gaussian']),
    'Methodology Function': strs_as_keys(['glm', 'betareg', 'polr_tolerant', 'multinom', 'stan_glm', 'stan_betareg', 'stan_polr']),
    'Data Feature': adjacencies_lossy_reverse({ # Reverse-direction definition here since more readable i.e. defining the contents of the lists
        'Binomial': ['Binary', 'Integer', '[0,1]', 'Boolean'],
        'Poisson': ['Non-Negative', 'Integer', 'Consecutive', 'Counts-Like'],
        'Multinomial': ['Factor', 'Consecutive', 'Non-Negative', 'Integer'],
        'Normal': ['Integer', 'Real', '+ and -'],
        'Beta': ['Real', '[0,1]'],
        'gamma': ['Non-Negative', 'Integer', 'Real', 'Non-Zero'],
        'Inverse Gaussian': ['Non-Negative', 'Integer', 'Real', 'Non-Zero'],
        'polr_tolerant': ['Consecutive']
    })
}

gsm = GSM(Graph(_shorthand_graph), {'Starting': ['Non-Negative', 'Non-Zero', 'Integer'], 'Added': [], 'From Steps': []}, by_score(presence_score), list_in_dict_accumulator('From Steps'), dict_fields_getter())

# gsm.plot()
# gsm.plot(layout = nx.shell_layout, radial_labels = True)
# gsm.plot(plotly = False)

gsm.consecutive_steps(dict(node_types = ['Distribution']), dict(node_types = ['Family Implementation']))
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