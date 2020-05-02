import matplotlib.pyplot as plt
import pandas as pd


def get_color_virus_status(s):
    if s == 'Susceptible':
        return 'lightblue'
    elif s == 'Infected':
        return 'gray'
    elif s == 'Recovered_Immune':
        return 'lightgreen'
    elif s == 'Death':
        return 'black'
    elif s == 'Hospitalization':
        return 'orange'
    elif s == 'Severe':
        return 'red'

    return 'white'


def get_color_wealth_status(a):
    if a == 'Q1':
        return 'red'
    elif a == 'Q2':
        return 'orange'
    elif a == 'Q3':
        return 'yellow'
    elif a == 'Q4':
        return 'green'

    return 'blue'


def update_statistics(sim, statistics):
    stats1 = sim.get_statistics(kind='info')
    statistics['info'].append(stats1)
    df1 = pd.DataFrame(statistics['info'], columns=[k for k in stats1.keys()])

    stats2 = sim.get_statistics(kind='ecom')
    statistics['ecom'].append(stats2)
    df2 = pd.DataFrame(statistics['ecom'], columns=[k for k in stats2.keys()])

    return df1, df2


def update(sim, virus_plot_lines, wealth_plot_lines, statistics):
    sim.execute()

    df1, df2 = update_statistics(sim, statistics)

    for col in virus_plot_lines.keys():
        virus_plot_lines[col].set_data(df1.index.values, df1[col].values)

    for col in wealth_plot_lines.keys():
        wealth_plot_lines[col].set_data(df2.index.values, df2[col].values)


def plot_simulation(sim, iterations):
    fig, ax = plt.subplots(nrows=2, ncols=1)

    # setup static first plot
    ax[0].set_title('Contagion evolution')
    ax[0].set_xlim((0, iterations))
    ax[0].set_xlabel("days")
    ax[0].set_ylabel("% of population")
    ax[0].axhline(y=sim.critical_limit, c="black", ls='--', label='Hospitalization limit')

    # setup static second plot
    ax[1].set_title('Economical impact')
    ax[1].set_xlim((0, iterations))
    ax[1].set_xlabel("days")
    ax[1].set_ylabel("wealth")

    statistics = {'info': [], 'ecom': []}
    sim.initialize()
    df1, df2 = update_statistics(sim, statistics)

    # setup dynamic first plot
    virus_plot_lines = {}
    for col in df1.columns.values:
        if col != 'Asymptomatic':
            virus_plot_lines[col], = ax[0].plot(df1.index.values, df1[col].values, c=get_color_virus_status(col),
                                                label=col)

    handles, labels = ax[0].get_legend_handles_labels()
    ax[0].legend(handles, labels)

    # setup dynamic second plot
    wealth_plot_lines = {}
    legend_ecom = {'Q1': 'Most Poor', 'Q2': 'Poor', 'Q3': 'Working Class', 'Q4': 'Rich', 'Q5': 'Most Rich'}
    for col in df2.columns.values:
        wealth_plot_lines[col], = ax[1].plot(df2.index.values, df2[col].values, c=get_color_wealth_status(col),
                                             label=legend_ecom[col])
    handles, labels = ax[1].get_legend_handles_labels()
    ax[1].legend(handles, labels)

    # simulate and update plots
    for _ in range(iterations):
        update(sim, virus_plot_lines, wealth_plot_lines, statistics)

    # show
    plt.show()
