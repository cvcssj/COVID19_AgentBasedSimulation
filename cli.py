from covid_abs.agents import Status, Position
from covid_abs.graphics import plot_simulation
from covid_abs.sim import Simulation


def main():
    initial_population = {
        Status.Protected: 20,
        Status.Exposed: 10,
        Status.Infected: 20,
        Status.Confirmed: 10,
        Status.Recovered: 0,
        Status.Dead: 0
    }  # in percentage

    simulation = Simulation(
        initial_population,
        population_size=200,
        contagion_distance=5,  # minimal distance between agents for contagion
        hospitalization_limit=0.05,  # maximum ratio of population which Healthcare System can handle simutaneously
        amplitudes={  # mobility ranges for agents, by Status
            Status.Susceptible: 5,
            Status.Recovered: 5,
            Status.Infected: 5
        }
    )

    simulation.append_trigger_population(
        lambda a: a.age >= 60,
        'move',
        lambda a: Position(a.position.x, a.position.y)
    )  # 60+ stay at home
    simulation.append_trigger_population(
        lambda agent1, agent2: agent1.age >= 60,
        'contact',
        lambda a: Status.Recovered
    )  # no contact between 60+ people and others

    plot_simulation(simulation, iterations=50)


if __name__ == '__main__':
    main()
