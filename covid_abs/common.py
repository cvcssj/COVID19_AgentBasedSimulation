
import numpy as np

"""
Probability of each infection serverity by age

Source: Imperial College Covid-19 research team, https://www.thelancet.com/action/showPdf?pii=S1473-3099%2820%2930243-7
"""

# probability of going to be hospitalized given that you're asymptomatic
age_hospitalization_probs = [0.001, 0.003, 0.012, 0.032, 0.049, 0.102, 0.166, 0.243, 0.273]

# probability of going to be in emergency room given that you're hospitalized
age_severe_probs = [0.05, 0.05, 0.05, 0.05, 0.063, 0.122, 0.274, 0.432, 0.709]

# probability of dying (at any time)
age_death_probs = [0.0000161, 0.0000695, 0.000309, 0.000844, 0.00161, 0.00595, 0.0193, 0.0428, 0.078]

# number of time iterations (e.g days) after which you're recovered from the virus (given that you took it before)
virus_in_body_until_recovered = 21

## Citar fontes

"""
Wealth distribution - Lorenz Curve

By quintile, source: https://www.worldbank.org/en/topic/poverty/lac-equity-lab1/income-inequality/composition-by-quintile
"""

lorenz_curve = [.04, .08, .13, .2, .56]
share = np.min(lorenz_curve)
basic_income = np.array(lorenz_curve)/share