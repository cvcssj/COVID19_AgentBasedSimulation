import numpy as np

from .agents import Status, InfectionSeverity, Agent, Position
from .data import LORENZ_CURVE, N_QUINTILS


class Simulation(object):
    def __init__(self, initial_population, population_size, length=100, height=100, minimum_income=1, minimum_expense=1,
                 *args, **kwargs):
        self.agents = []
        self.population_size = population_size
        self.initial_population = initial_population

        self.length = length
        self.height = height

        self.minimum_income = minimum_income
        self.minimum_expense = minimum_expense

        self.contagion_distance = kwargs.get('contagion_distance', 1.)
        self.contagion_rate = kwargs.get('contagion_rate', 0.9)
        self.hospitalization_limit = kwargs.get('critical_limit', 0.6)
        self.amplitudes = kwargs.get('amplitudes', {
            Status.Susceptible: 5,
            Status.Recovered: 5,
            Status.Infected: 5
        })

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
        self.agents.append(self._random_agent(status, position))

    def _create_agents(self, status, n, positions=None):
        if positions is None:
            positions = [None for _ in range(n)]

        for i in range(n):
            self.agents.append(self._random_agent(status, positions[i]))

    def _init_population(self):
        for status, percentage in self.initial_population.items():
            n_people = percentage * self.population_size
            self._create_agents(status, n_people)

        n_people_left = self.population_size - len(self.agents)  # the rest
        self._create_agents(Status.Susceptible, n_people_left)

    def _init_wealth(self, wealth=1e4):
        for i, quintil in enumerate(LORENZ_CURVE):  # share common wealth
            total = quintil * wealth
            such_agents = self._get_agents(lambda x: x.social_stratum == i and x.is_adult())
            total_per_quintil = len(such_agents)

            qty = max(1.0, total_per_quintil)
            avg = total / qty
            for agent in such_agents:
                agent.wealth = avg

    def init(self):
        self._init_population()
        self._init_wealth()

    def _n_hospitalized(self):
        n_severe = self.statistics[InfectionSeverity.Severe.name]
        n_light = self.statistics[InfectionSeverity.Hospitalization.name]
        return n_severe + n_light

    def update_status(self):
        self._recompute_statistics()
        self.are_there_places_in_hospital = self._n_hospitalized() < self.hospitalization_limit

    def _get_interactions(self):
        for i in np.arange(0, self.population_size):
            for j in np.arange(i + 1, self.population_size):
                ai = self.agents[i]
                aj = self.agents[j]
                if ai.will_make_contact(aj, self.contagion_distance):
                    yield (ai, aj)

    def _execute_move(self):
        triggers = [k for k in self.triggers_population if k['attribute'] == 'move']
        for agent in self.agents:
            agent.move(self.length, self.height, self.amplitudes, self.minimum_expense, triggers)
            agent.update(self.are_there_places_in_hospital, self.minimum_expense)

        self.update_status()  # for each move -> update status

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
        return list(filter(filter_by, self.agents))

    def _recompute_statistics(self):
        self._reset_statistics()

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

    def get_statistics(self, kind='info'):
        if self.statistics is None:
            self._recompute_statistics()

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
