
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
    'Data Feature': dict(
        {'Constant': []},
        **adjacencies_lossy_reverse({ # Reverse-direction definition here since more readable i.e. defining the contents of the lists
            'Binomial': ['Binary', 'Integer', '[0,1]', 'Boolean'],
            'Poisson': ['Non-Negative', 'Integer', 'Non-Zero'],
            'Multinomial': ['Factor', 'Consecutive', 'Non-Negative', 'Integer'],
            'Normal': ['Integer', 'Real'],
            'Beta': ['Real', '[0,1]'],
            'Gamma D': ['Non-Negative', 'Real', 'Non-Zero']
        })
    )
}

gsm = GSM(Graph(_shorthand_graph), {'Starting': ['Non-Negative', 'Non-Zero', 'Integer'], 'Added': [], 'From Steps': []}, by_score(presence_score), list_in_dict_accumulator('From Steps'), dict_fields_getter())

# gsm.plot()

gsm.consecutive_steps(['Distribution', 'Family Implementation']) # Perform 2 steps
print(gsm._scan('Method Function')) # Peek at intermediate value of new a step
gsm.step('Method Function') # Perform the step
gsm.step('NON EXISTING TYPE') # Trigger a warning and no State changes

print(gsm)