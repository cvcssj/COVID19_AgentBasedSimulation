import numpy as np

from .agents import Status, InfectionSeverity, Agent, Position
from .data import LORENZ_CURVE


class Simulation(object):
    def __init__(self, **kwargs):
        self.population = []
        self.population_size = kwargs.get("population_size", 20)
        self.length = kwargs.get("length", 10)
        self.height = kwargs.get("height", 10)
        self.initial_infected_perc = kwargs.get("initial_infected_perc", 0.05)
        self.initial_immune_perc = kwargs.get("initial_immune_perc", 0.05)
        self.contagion_distance = kwargs.get("contagion_distance", 1.)
        self.contagion_rate = kwargs.get("contagion_rate", 0.9)
        self.critical_limit = kwargs.get("critical_limit", 0.6)
        self.amplitudes = kwargs.get('amplitudes',
                                     {Status.Susceptible: 5,
                                      Status.Recovered_Immune: 5,
                                      Status.Infected: 5})
        self.minimum_income = kwargs.get("minimum_income", 1.0)
        self.minimum_expense = kwargs.get("minimum_expense", 1.0)
        self.statistics = None
        self.triggers_simulation = kwargs.get("triggers_simulation", [])
        self.triggers_population = kwargs.get("triggers_population", [])

    def append_trigger_simulation(self, condition, attribute, action):
        self.triggers_simulation.append({'condition': condition, 'attribute': attribute, 'action': action})

    def append_trigger_population(self, condition, attribute, action):
        self.triggers_population.append({'condition': condition, 'attribute': attribute, 'action': action})

    def _random_position(self):
        x = np.clip(int(self.length / 2 + (np.random.randn(1) * (self.length / 3))),
                    0, self.length)
        y = np.clip(int(self.height / 2 + (np.random.randn(1) * (self.height / 3))),
                    0, self.height)
        return Position(x, y)

    def _random_agent(self, status, position=None):
        if position is None:
            position = self._random_position()
        return Agent.create_random(position, status)

    def create_agent(self, status, position=None):
        self.population.append(self._random_agent(status, position))

    def initialize(self):
        # Initial infected population
        for _ in np.arange(0, int(self.population_size * self.initial_infected_perc)):
            self.create_agent(Status.Infected)

        # Initial immune population
        for _ in np.arange(0, int(self.population_size * self.initial_immune_perc)):
            self.create_agent(Status.Recovered_Immune)

        # Initial susceptible population
        for _ in np.arange(0, self.population_size - len(self.population)):
            self.create_agent(Status.Susceptible)

        # Share the common wealth of 10^4 among the population, according each agent social stratum
        wealth = 10 ** 4
        for quintil in [0, 1, 2, 3, 4]:
            total = LORENZ_CURVE[quintil] * wealth
            qty = max(1.0, np.sum([1 for a in self.population if a.social_stratum == quintil and a.age >= 18]))
            share = total / qty
            for agent in filter(lambda x: x.social_stratum == quintil and x.age >= 18, self.population):
                agent.wealth = share

    def contact(self, agent1, agent2, triggers=None):
        if triggers is None:
            triggers = []

        for trigger in triggers:
            if trigger['condition'](agent1, agent2):
                agent1.status = trigger['action'](agent1)
                return

        if agent1.status == Status.Susceptible and agent2.status == Status.Infected:
            test_contagion = np.random.random()
            if test_contagion <= self.contagion_rate:
                agent1.status = Status.Infected

    def move(self, agent, triggers=None):
        agent.move(self.length, self.height, self.amplitudes, self.minimum_expense, triggers)

    def update(self, agent):
        self.get_statistics()
        total_in_hospital = self.statistics['Severe'] + self.statistics['Hospitalization']
        are_there_places_in_hospital = total_in_hospital < self.critical_limit
        agent.update(are_there_places_in_hospital, self.minimum_expense)

    def execute(self):
        mov_triggers = [k for k in self.triggers_population if k['attribute'] == 'move']
        con_triggers = [k for k in self.triggers_population if k['attribute'] == 'contact']
        other_triggers = [k for k in self.triggers_population if
                          k['attribute'] != 'move' and k['attribute'] != 'contact']

        for agent in self.population:
            self.move(agent, triggers=mov_triggers)
            self.update(agent)

            for trigger in other_triggers:
                if trigger['condition'](agent):
                    attr = trigger['attribute']
                    agent.__dict__[attr] = trigger['action'](agent.__dict__[attr])

        contacts = []

        for i in np.arange(0, self.population_size):
            for j in np.arange(i + 1, self.population_size):
                ai = self.population[i]
                aj = self.population[j]
                too_near = ai.distance(aj) <= self.contagion_distance

                if too_near:
                    contacts.append((i, j))

        for par in contacts:
            ai = self.population[par[0]]
            aj = self.population[par[1]]
            self.contact(ai, aj, triggers=con_triggers)
            self.contact(aj, ai, triggers=con_triggers)

        if len(self.triggers_simulation) > 0:
            for trigger in self.triggers_simulation:
                if trigger['condition'](self):
                    attr = trigger['attribute']
                    self.__dict__[attr] = trigger['action'](self.__dict__[attr])

        self.statistics = None

    def get_positions(self):
        return [[a.x, a.y] for a in self.population]

    def get_statistics(self, kind='info'):
        if self.statistics is None:
            self.statistics = {}
            for status in Status:
                self.statistics[status.name] = np.sum(
                    [1 for a in self.population if a.status == status]) / self.population_size

            for infected_status in InfectionSeverity:
                self.statistics[infected_status.name] = np.sum([1 for a in self.population if
                                                                a.infected_status == infected_status and a.status != Status.Death]) / self.population_size

            for quintil in [0, 1, 2, 3, 4]:
                self.statistics['Q{}'.format(quintil + 1)] = np.sum(
                    [a.wealth for a in self.population if a.social_stratum == quintil \
                     and a.age >= 18 and a.status != Status.Death])

        return self.filter_stats(kind)

    def filter_stats(self, kind):
        if kind == 'info':
            return {k: v for k, v in self.statistics.items() if not k.startswith('Q')}
        elif kind == 'ecom':
            return {k: v for k, v in self.statistics.items() if k.startswith('Q')}
        else:
            return self.statistics
