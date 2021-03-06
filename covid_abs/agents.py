from collections import namedtuple
from enum import Enum

import numpy as np

from data import PROB_HOSP, PROB_HOSP_ICU, PROB_DIE, N_VIRUS_RECOVERY, BASIC_INCOME, N_QUINTILS


class Status(Enum):
    Protected = 'P'
    Susceptible = 'S'
    Exposed = 'E'
    Infected = 'Ia'
    Confirmed = 'Iq'
    Recovered = 'R'
    Dead = 'D'


Position = namedtuple('Position', 'x y')


class Agent(object):
    def __init__(self, **kwargs):
        self.position = kwargs.get('position', Position(x=0, y=0))
        self.status = kwargs.get('status', Status.Susceptible)
        self.age = kwargs.get('age', 0)
        self.social_stratum = kwargs.get('social_stratum', 0)
        self.wealth = kwargs.get('wealth', 0.0)
        self.stat_index = int(self.age) // 10 - 1 if self.age > 10 else 0  # index to access arrays with statistics

    def update(self, are_there_places_in_hospital, minimum_expense):
        if self.status == Status.Dead:
            return

        if self.status == Status.Infected:
            self.infected_time += 1
            teste_sub = np.random.random()

            if self.infected_status == InfectionSeverity.Asymptomatic:
                if PROB_HOSP[self.stat_index] > teste_sub:
                    self.infected_status = InfectionSeverity.Hospitalization
            elif self.infected_status == InfectionSeverity.Hospitalization:
                if PROB_HOSP_ICU[self.stat_index] > teste_sub:
                    self.infected_status = InfectionSeverity.Severe
                    if not are_there_places_in_hospital:
                        self.status = Status.Dead  # die because there is no place in the hospitals
                        self.infected_status = InfectionSeverity.Asymptomatic

            if self.status.name == Status.Infected:
                death_test = np.random.random()
                if PROB_DIE[self.stat_index] > death_test:
                    self.status = Status.Dead
                    self.infected_status = InfectionSeverity.Asymptomatic
                    return

            if self.infected_time > N_VIRUS_RECOVERY:
                self.infected_time = 0
                self.status = Status.Recovered
                self.infected_status = InfectionSeverity.Asymptomatic

        self.wealth -= minimum_expense * BASIC_INCOME[self.social_stratum]

    def _move(self, ix, iy, max_length, max_height):
        if (self.position.x + ix) <= 0 or (self.position.x + ix) >= max_length:
            self.position = Position(self.position.x - ix, self.position.y)
        else:
            self.position = Position(self.position.x + ix, self.position.y)

        if (self.position.y + iy) <= 0 or (self.position.y + iy) >= max_height:
            self.position = Position(self.position.x, self.position.y - iy)
        else:
            self.position = Position(self.position.x, self.position.y + iy)

    def _update_wealth(self, ix, iy, minimum_expense):
        dist = np.sqrt(ix ** 2 + iy ** 2)
        result_ecom = np.random.rand(1)
        self.wealth += dist * result_ecom * minimum_expense * BASIC_INCOME[self.social_stratum]

    def move(self, max_length, max_height, amplitudes, minimum_expense, triggers=None):
        if triggers is None:
            triggers = []

        is_dead = self.status == Status.Dead
        is_infected = self.status == Status.Infected
        is_hospitalized = self.infected_status == InfectionSeverity.Hospitalization or self.infected_status == InfectionSeverity.Severe
        if is_dead or (is_infected and is_hospitalized):
            return

        for trigger in triggers:
            if trigger['condition'](self):
                self.position = trigger['action'](self)
                return

        ix = int(np.random.randn(1) * amplitudes[self.status])
        iy = int(np.random.randn(1) * amplitudes[self.status])
        self._move(ix, iy, max_length, max_height)
        self._update_wealth(ix, iy, minimum_expense)

    def distance(self, other):
        return np.sqrt((self.position.x - other.position.x) ** 2 + (self.position.y - other.position.y) ** 2)

    def will_make_contact(self, other, contagion_distance):
        return self.distance(other) <= contagion_distance

    def interact(self, other, contagion_rate, triggers=None):
        if triggers is None:
            triggers = []

        for trigger in triggers:
            if trigger['condition'](self, other):
                self.status = trigger['action'](self)
                return

        if self.status == Status.Susceptible and other.status == Status.Infected:
            test_contagion = np.random.random()
            if test_contagion <= contagion_rate:
                self.status = Status.Infected

    def get_summary(self):
        return '{} yo, {} class, {} $: {}'.format(self.age, self.social_stratum, self.wealth, self.status.name)

    def is_alive(self):
        return self.status != Status.Dead

    def is_dead(self):
        return not self.is_alive()

    def is_adult(self):
        return self.age >= 18

    def __str__(self):
        return str(self.status.name)

    @staticmethod
    def create_random(position, status):
        age = np.random.beta(2, 5, 1) * 100
        social_stratum = np.random.randint(0, N_QUINTILS)
        return Agent(position=position, age=age, status=status, social_stratum=social_stratum)
