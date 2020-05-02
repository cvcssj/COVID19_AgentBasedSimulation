import matplotlib.pyplot as plt
import pandas as pd

from .agents import Status, InfectionSeverity

legend_ecom = {'Q1': 'Most Poor', 'Q2': 'Poor', 'Q3': 'Working Class', 'Q4': 'Rich', 'Q5': 'Most Rich'}


def color1(s):
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
    else:
        return 'white'


def color2(agent):
    if agent.status == Status.Susceptible:
        return 'lightblue'
    elif agent.status == Status.Infected:
        if agent.infected_status == InfectionSeverity.Asymptomatic:
            return 'gray'
        elif agent.infected_status == InfectionSeverity.Hospitalization:
            return 'orange'
        else:
            return 'red'
    elif agent.status == Status.Recovered_Immune:
        return 'lightgreen'
    elif agent.status == Status.Death:
        return 'black'


def color3(a):
    if a == 'Q1':
        return 'red'
    elif a == 'Q2':
        return 'orange'
    elif a == 'Q3':
        return 'yellow'
    elif a == 'Q4':
        return 'green'
    elif a == 'Q5':
        return 'blue'


def update_statistics(sim, statistics):
    stats1 = sim.get_statistics(kind='info')
    statistics['info'].append(stats1)
    df1 = pd.DataFrame(statistics['info'], columns=[k for k in stats1.keys()])

    stats2 = sim.get_statistics(kind='ecom')
    statistics['ecom'].append(stats2)
    df2 = pd.DataFrame(statistics['ecom'], columns=[k for k in stats2.keys()])

    return df1, df2


def clear(scat, linhas1, linhas2):
    """

    :param scat:
    :param linhas1:
    :param linhas2:
    :return:
    """
    for linha1 in linhas1.values():
        linha1.set_data([], [])

    for linha2 in linhas2.values():
        linha2.set_data([], [])

    ret = [scat]
    for l in linhas1.values():
        ret.append(l)
    for l in linhas2.values():
        ret.append(l)

    return tuple(ret)


def update(sim, linhas1, linhas2, statistics):
    """
    Execute an iteration of the simulation and update the animation graphics

    :param sim:
    :param scat:
    :param linhas1:
    :param linhas2:
    :param statistics:
    :return:
    """

    sim.execute()

    df1, df2 = update_statistics(sim, statistics)

    for col in linhas1.keys():
        linhas1[col].set_data(df1.index.values, df1[col].values)

    for col in linhas2.keys():
        linhas2[col].set_data(df2.index.values, df2[col].values)


def plot_simulation(sim, iterations):
    fig, ax = plt.subplots(nrows=2, ncols=1)

    # setup static first plot
    ax[0].set_title('Contagion Evolution')
    ax[0].set_xlim((0, iterations))
    ax[0].set_xlabel("days")
    ax[0].set_ylabel("% of population")
    ax[0].axhline(y=sim.critical_limit, c="black", ls='--', label='Critical limit')

    # setup static second plot
    ax[1].set_title('Economical impact')
    ax[1].set_xlim((0, iterations))
    ax[1].set_xlabel("days")
    ax[1].set_ylabel("wealth")

    statistics = {'info': [], 'ecom': []}
    sim.initialize()
    df1, df2 = update_statistics(sim, statistics)

    # setup dynamic first plot
    linhas1 = {}
    for col in df1.columns.values:
        if col != 'Asymptomatic':
            linhas1[col], = ax[0].plot(df1.index.values, df1[col].values, c=color1(col), label=col)

    handles, labels = ax[0].get_legend_handles_labels()
    ax[0].legend(handles, labels, loc='upper right')  # 2, bbox_to_anchor=(0, 0))

    # setup dynamic second plot
    linhas2 = {}
    for col in df2.columns.values:
        linhas2[col], = ax[1].plot(df2.index.values, df2[col].values, c=color3(col), label=legend_ecom[col])
    handles, labels = ax[1].get_legend_handles_labels()
    ax[1].legend(handles, labels, loc='upper right')  # 2, bbox_to_anchor=(1, 1))

    # simulate and update plots
    for _ in range(iterations):
        update(sim, linhas1, linhas2, statistics)

    # show
    plt.show()


def save_gif(anim, file):
    anim.save(file, writer='imagemagick', fps=60)
