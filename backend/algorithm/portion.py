import random
import time
from math import exp

from django.conf import settings

from backend.algorithm.common import Nutrition
from backend.algorithm.requirements import SMALL_PORTION_MAX, LARGE_PORTION_MAX, nutritional_info_for
from backend.models import MealItem, StudentProfile


def mean(a, b):
    return (a + b) / 2


def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x


def move_value(x, c, l, r):
    """
    "Moves" a value x to some value within a ratio c of itself within the borders [l, r]

    Note that "c" in this case should be a decimal (i.e. c=0.01 -> 1%)
    """

    s = 1 - 2 * random.randint(0, 1)  # random sign
    return clamp(x + c * (r - l) * s, l, r)


def neighbour(state, t):
    l, s1, s2 = state
    rnd = random.randint(0, 2)
    if rnd == 0:
        return move_value(l, t, LARGE_PORTION_MAX / 2, LARGE_PORTION_MAX), s1, s2
    elif rnd == 1:
        return l, move_value(s1, t, SMALL_PORTION_MAX / 2, SMALL_PORTION_MAX), s2
    else:
        return l, s1, move_value(s2, t, SMALL_PORTION_MAX / 2, SMALL_PORTION_MAX)


# Source: https://en.wikipedia.org/wiki/Simulated_annealing#Overview
# https://codeforces.com/blog/entry/94437
# I am peak intuition
class SimulatedAnnealing:
    def __init__(self, profile: StudentProfile, large: MealItem, small1: MealItem, small2: MealItem,
                 alpha: float = 0.999, smallest_temp: float = 0.0005):
        # Info properties
        self.lo_req, self.hi_req = nutritional_info_for(profile)
        self.l_nut = Nutrition.from_meal_item(large) / large.portion_volume
        self.s1_nut = Nutrition.from_meal_item(small1) / small1.portion_volume
        self.s2_nut = Nutrition.from_meal_item(small2) / small2.portion_volume

        # Parameter properties
        self.alpha = alpha
        self.smallest_temp = smallest_temp

        # State properties
        self.t = 1
        self.state = (0, 0, 0)

        # Result properties
        self.done = False
        self.final_cost = -1
        self.runtime = -1

    def mid_state(self):
        """
        Forces the state to be in the middle value
        """
        return 0.75 * LARGE_PORTION_MAX, 0.75 * SMALL_PORTION_MAX, 0.75 * SMALL_PORTION_MAX

    def lo_state(self):
        """
        Returns the minimum possible state
        """
        return LARGE_PORTION_MAX / 2, SMALL_PORTION_MAX / 2, SMALL_PORTION_MAX / 2

    def hi_state(self):
        """
        Returns the maximum possible state
        """
        return LARGE_PORTION_MAX, SMALL_PORTION_MAX, SMALL_PORTION_MAX

    def nutrition_of(self, state: tuple[float, float, float]):
        ret = Nutrition()
        ret += self.l_nut * state[0]
        ret += self.s1_nut * state[1]
        ret += self.s2_nut * state[2]
        return ret

    def cost_of(self, state):
        cur_info = self.nutrition_of(state)
        res = 0

        def dist_sq(x, l, r):
            if x < l: return (l - x) ** 2
            elif r < x: return (x - r) ** 2
            return 0

        # For macros, the weights are (generally) the amount of calories in each item
        res += dist_sq(cur_info.calories, self.lo_req.calories, self.hi_req.calories)
        res += 8 * dist_sq(cur_info.carbohydrate, self.lo_req.carbohydrate, self.hi_req.carbohydrate)
        res += 20 * dist_sq(cur_info.carbohydrate, self.lo_req.carbohydrate, self.hi_req.carbohydrate)
        res += 50 * dist_sq(cur_info.total_fat, self.lo_req.total_fat, self.hi_req.total_fat)
        res += 1.5 * 50 * dist_sq(cur_info.saturated_fat, self.lo_req.saturated_fat, self.hi_req.saturated_fat)
        res += 50 * dist_sq(cur_info.trans_fat, self.lo_req.trans_fat, self.hi_req.trans_fat)

        # # For the rest... I'm kinda just yoloing this ngl...
        # res += 3 * (cur_info.sugar - self.req.sugar) ** 2
        # res += 0.1 * (cur_info.cholesterol - self.req.cholesterol)
        # res += 4 * (cur_info.fiber - self.req.fiber)
        # res += 0.2 * (cur_info.sodium - self.req.sodium)
        # res += 0.1 * (cur_info.potassium - self.req.potassium)
        # res += 0.15 * (cur_info.calcium - self.req.calcium)
        # res += 0.5 * (cur_info.iron - self.req.iron)
        #
        # # Vitamins!!!
        # res += 0.1 * max(0., self.req.vitamin_c - cur_info.vitamin_c) ** 2
        # res += 0.1 * max(0., self.req.vitamin_d - cur_info.vitamin_d) ** 2
        # res += 0.1 * max(0., self.req.vitamin_a - cur_info.vitamin_a) ** 2

        return res

    def accept_probability_of(self, next_state, cur_state, scale_coeff):
        c_new = self.cost_of(next_state)
        c_old = self.cost_of(cur_state)
        return 1 if c_new <= c_old else exp(-(c_new - c_old) * scale_coeff / self.t)

    def run_algorithm(self):
        # set RNG
        if settings.PROD:
            random.seed(20210226)

        # Initialization
        cost_bound = max(self.cost_of(self.lo_state()), self.cost_of(self.hi_state()))
        scale_cost_by = 60 / cost_bound
        self.state = self.mid_state()

        # Run algorithm
        start_time = time.perf_counter()
        t = 0.6  # Initial Temp
        while t >= self.smallest_temp:
            t *= self.alpha
            state_new = neighbour(self.state, t)
            if self.accept_probability_of(state_new, self.state, scale_cost_by) >= random.random():
                self.state = state_new

        # Set result vars
        self.runtime = time.perf_counter() - start_time
        self.final_cost = self.cost_of(self.state)
        self.done = True

    # Some result properties
    @property
    def large_volume(self):
        return self.state[0]

    @property
    def small1_volume(self):
        return self.state[1]

    @property
    def small2_volume(self):
        return self.state[2]
