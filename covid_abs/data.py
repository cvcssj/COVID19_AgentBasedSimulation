import numpy as np

# p(Asymp -> Hosp)
# see https://www.thelancet.com/action/showPdf?pii=S1473-3099%2820%2930243-7
PROB_HOSP = [
    0.001,  # 0-9
    0.003,  # 10-19
    0.012,  # 20-29
    0.032,  # 30-39
    0.049,  # 40-49
    0.102,  # 50-59
    0.166,  # 60-69
    0.243,  # 70-79
    0.273  # 80+
]

# p(Hosp -> ICU)
PROB_HOSP_ICU = [
    0.05,  # 0-9
    0.05,  # 10-19
    0.05,  # 20-29
    0.05,  # 30-39
    0.063,  # 40-49
    0.122,  # 50-59
    0.274,  # 60-69
    0.432,  # 70-79
    0.709  # 80+
]

# # p(Die)
PROB_DIE = [
    0.0000161,  # 0-9
    0.0000695,  # 10-19
    0.000309,  # 20-29
    0.000844,  # 30-39
    0.00161,  # 40-49
    0.00595,  # 50-59
    0.0193,  # 60-69
    0.0428,  # 70-79
    0.078  # 80+
]

# # days after which you're recovered from the virus (given that you took it before)
N_VIRUS_RECOVERY = 21

# Wwealth distribution (lorenz curve)
LORENZ_CURVE = [
    .04,  # 20 %
    .08,  # 40 %
    .13,  # 60 %
    .2,  # 80 %
    .56  # 100 %
]
N_QUINTILS = 5
BASIC_INCOME = np.array(LORENZ_CURVE) / np.min(LORENZ_CURVE)
