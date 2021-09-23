
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

gsm = GSM(Graph(_shorthand_graph), ['Non-Negative', 'Non-Zero', 'Integer']) # Using default function-arguments
    # The default node_scanner is by jaccard similarity score, and supports 4 additional arguments to filter candidates
    # and their neighbours by type; only the first one (candidate type list) is used in the examples below

# gsm.plot()

gsm.consecutive_steps(dict(node_types = ['Distribution']), dict(node_types = ['Family Implementation']))
    # Perform 2 steps, giving one optional argument (incidentally, the first one) for each step,
    # i.e. the (singleton) list of types to focus on

# gsm.consecutive_steps([['Distribution']], [['Family Implementation']]) # Unnamed-arguments version of the above
# gsm.parallel_steps([['Distribution']], [['Family Implementation']]) # Parallel version, warning of failure for 'Family Implementation'
print(gsm.log[-1], '\n') # Can check the log for details of the last step

print(gsm._scan(['Method Function']), '\n') # Can also peek ahead at the intermediate value of a possible next step
gsm.step(['Method Function']) # Perform the step

gsm.step(['NON EXISTING TYPE']) # Trigger a warning and no State changes
print(gsm.log[-1], '\n') # The failed step is also logged

print(gsm)