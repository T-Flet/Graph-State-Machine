import matplotlib.pyplot as plt

from Graph_State_Machine.gsm import Graph, GSM
from Graph_State_Machine.Util.misc import adjacencies_lossy_reverse, strs_as_keys

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

gsm = GSM(Graph(_shorthand_graph), ['Non-Negative', 'Non-Zero', 'Integer']) # Default function-arguments

gsm.plot()

gsm.consecutive_steps(['Distribution', 'Family Implementation']) # Perform 2 steps
print(gsm._step_res('Method Function')) # Peek at intermediate value of new a step
gsm.step('Method Function') # Perform the step

print(gsm)
plt.show()
