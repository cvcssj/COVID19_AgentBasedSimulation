from covid_abs.abs import Simulation
from covid_abs.agents import Status
from covid_abs.graphics import plot_simulation


def main():
    sim = Simulation(
        length=100,  # mobility length (how much a particle can move x-wise)
        height=100,  # mobility height (how much a particle can move y-wise)
        initial_infected_perc=0.02,  # ratio of infected in initial population
        population_size=200,
        contagion_distance=5,  # minimal distance between agents for contagion
        critical_limit=5 / 100,  # maximum ratio of population which Healthcare System can handle simutaneously
        amplitudes={  # mobility ranges for agents, by Status
            Status.Susceptible: 5,
            Status.Recovered_Immune: 5,
            Status.Infected: 5
        })

    sim.append_trigger_population(
        lambda a: a.age >= 60,
        'move',
        lambda a: (a.x, a.y)
    )  # 60+ stay at home
    sim.append_trigger_population(
        lambda agent1, agent2: agent1.age >= 60,
        'contact',
        lambda a: Status.Recovered_Immune
    )  # no contact between 60+ people and others

    plot_simulation(sim, iterations=10)


if __name__ == '__main__':
    main()
