import numpy as np

from .agents import Status, InfectionSeverity, Agent, Position
from .data import LORENZ_CURVE, N_QUINTILS


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

        self.amplitudes = kwargs.get('amplitudes', {
            Status.Susceptible: 5,
            Status.Recovered: 5,
            Status.Infected: 5
        })

        self.minimum_income = kwargs.get("minimum_income", 1.0)
        self.minimum_expense = kwargs.get("minimum_expense", 1.0)

        self.statistics = None
        self.are_there_places_in_hospital = True
        self.triggers_population = []

    def append_trigger_population(self, condition, attribute, action):
        self.triggers_population.append({'condition': condition, 'attribute': attribute, 'action': action})

    def _random_position(self):
        x = np.random.uniform(0, self.length)
        y = np.random.uniform(0, self.height)
        return Position(x, y)

    def _random_agent(self, status, position=None):
        if position is None:
            position = self._random_position()
        return Agent.create_random(position, status)

    def _create_agent(self, status, position=None):
        self.population.append(self._random_agent(status, position))

    def create_agents(self, status, n, positions=None):
        if positions is None:
            positions = [None for _ in range(n)]

        for i in range(n):
            self.population.append(self._random_agent(status, positions[i]))

    def init(self):
        self._init_population()
        self._init_wealth()

    def _init_population(self):
        n = int(self.population_size * self.initial_infected_perc)
        self.create_agents(Status.Infected, n)

        n = int(self.population_size * self.initial_immune_perc)
        self.create_agents(Status.Recovered, n)

        n = self.population_size - len(self.population)  # the rest
        self.create_agents(Status.Susceptible, n)

    def _init_wealth(self, wealth=1e4):
        for i, quintil in enumerate(LORENZ_CURVE):  # share common wealth
            total = quintil * wealth
            agent_in_quintil = list(filter(lambda x: x.social_stratum == i and x.is_adult(), self.population))
            total_per_quintil = len(agent_in_quintil)

            qty = max(1.0, total_per_quintil)
            share = total / qty
            for agent in agent_in_quintil:
                agent.wealth = share

    def update_status(self):
        self.get_statistics()
        total_in_hospital = self.statistics['Severe'] + self.statistics['Hospitalization']
        self.are_there_places_in_hospital = total_in_hospital < self.critical_limit

    def _get_interactions(self):
        for i in np.arange(0, self.population_size):
            for j in np.arange(i + 1, self.population_size):
                ai = self.population[i]
                aj = self.population[j]
                if ai.will_make_contact(aj, self.contagion_distance):
                    yield (ai, aj)

    def _execute_move(self):
        triggers = [k for k in self.triggers_population if k['attribute'] == 'move']
        for agent in self.population:
            agent.move(self.length, self.height, self.amplitudes, self.minimum_expense, triggers)
            self.update_status()  # for each move -> update status
            agent.update(self.are_there_places_in_hospital, self.minimum_expense)

    def _execute_interactions(self):
        interactions = list(self._get_interactions())
        triggers = [k for k in self.triggers_population if k['attribute'] == 'contact']
        for (ai, aj) in interactions:
            ai.interact(aj, self.contagion_rate, triggers)
            aj.interact(ai, self.contagion_rate, triggers)

    def _reset_statistics(self):
        self.statistics = None

    def execute(self):
        self._execute_move()
        self._execute_interactions()
        self._reset_statistics()

    def _get_agents(self, filter_by):
        return list(filter(filter_by, self.population))

    def get_statistics(self, kind='info'):
        if self.statistics is None:
            self.statistics = {}
            for status in Status:
                such_agents = self._get_agents(lambda x: x.status == status)
                self.statistics[status.name] = len(such_agents) / self.population_size  # ratio

            for infected_status in InfectionSeverity:
                such_agents = self._get_agents(lambda x: x.infected_status == infected_status and x.is_alive())
                self.statistics[infected_status.name] = len(such_agents) / self.population_size  # ratio

            for q in range(N_QUINTILS):
                such_agents = self._get_agents(lambda x: x.social_stratum == q and x.is_adult() and x.is_alive())
                wealth = sum([a.wealth for a in such_agents])
                self.statistics['Q{}'.format(q + 1)] = wealth

        return self._get_stats(kind)

    def _get_virus_stats(self):
        return {k: v for k, v in self.statistics.items() if not k.startswith('Q')}

    def _get_wealth_stats(self):
        return {k: v for k, v in self.statistics.items() if k.startswith('Q')}

    def _get_stats(self, kind):
        if kind == 'info':
            return self._get_virus_stats()
        elif kind == 'ecom':
            return self._get_wealth_stats()

        return self.statistics
