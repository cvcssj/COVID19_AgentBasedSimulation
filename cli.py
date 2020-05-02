from covid_abs.agents import Status, Position
from covid_abs.graphics import plot_simulation
from covid_abs.sim import Simulation


def main():
    sim = Simulation(
        length=100,  # mobility length (how much a particle can move x-wise)
        height=100,  # mobility height (how much a particle can move y-\wise)
        initial_infected_perc=0.02,  # ratio of infected in initial population
        population_size=200,
        contagion_distance=5,  # minimal distance between agents for contagion
        critical_limit=5 / 100,  # maximum ratio of population which Healthcare System can handle simutaneously
        amplitudes={  # mobility ranges for agents, by Status
            Status.Susceptible: 5,
            Status.Recovered: 5,
            Status.Infected: 5
        }
    )

    sim.append_trigger_population(
        lambda a: a.age >= 60,
        'move',
        lambda a: Position(a.position.x, a.position.y)
    )  # 60+ stay at home
    sim.append_trigger_population(
        lambda agent1, agent2: agent1.age >= 60,
        'contact',
        lambda a: Status.Recovered
    )  # no contact between 60+ people and others

    plot_simulation(sim, iterations=50)


if __name__ == '__main__':
    main()
