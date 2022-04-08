import dataclasses
import math
import random
import time
from dataclasses import dataclass
from math import exp
from typing import Union

from django.conf import settings

from backend.algorithm.common import Nutrition
from backend.algorithm.requirements import nutritional_info_for
from backend.models import MealItem, StudentProfile


def clamp(x: float, a: float, b: float) -> float:
    if x < a:
        return a
    elif x > b:
        return b
    return x


def dist_sq(x: float, l: float, r: float) -> float:
    if x < l:
        return (l - x) ** 2
    elif r < x:
        return (x - r) ** 2
    return 0


def random_sign() -> int:
    """
    randomly returns -1 or 1
    """
    return 1 - 2 * random.randint(0, 1)  # random sign


def ceil_div(a: int, b: int) -> int:
    """
    Ceiling division with integers.  Only works for non-negative
    """
    return (a + b - 1) // b


@dataclass
class PlateSectionState:
    nutrition: Nutrition
    volume: Union[float, int]
    portion_volume: Union[float, int]
    max_volume: Union[float, int]
    section_name: str
    discrete: bool

    @classmethod
    def from_meal_item(cls, item: MealItem, container_volume: float, num_sections: int, section_name: str):
        """
        Creates a PlateSectionState (with 0 cur. volume) from a given meal item and other parameters
        @param item The meal item to create the object from
        @param container_volume The total container volume, in DB format (i.e. positive for continuous, negative integer for discrete)
        @param num_sections The number of sections this container is divided into (so the actual volume can be computed by how much of the section this occupies)
        @param section_name The name of the section (currently, "large", "small1", or "small2")
        """
        discrete = item.portion_volume < 0
        if discrete:
            volume = 0
            portion_volume = ceil_div(int(abs(round(item.portion_volume))), num_sections)
            max_volume = item.max_pieces
        else:
            volume = 0.
            portion_volume = item.portion_volume
            max_volume = container_volume / num_sections

        return cls(Nutrition.from_meal_item(item), volume, portion_volume, max_volume, section_name, discrete)

    @property
    def min_volume(self):
        """
        Returns the min volume instead of the max volume
        """
        return max(1, ceil_div(self.max_volume, 2)) if self.discrete else self.max_volume / 2

    def scaled_nutrition(self):
        """
        Returns the nutrition facts scaled by the portion volume
        """
        return self.nutrition * (self.volume / self.portion_volume)

    def format_volume(self):
        """
        Returns the volume of the item but formatted properly (i.e. discrete volumes are negative
        """
        return self.volume if not self.discrete else float(-self.volume)

    def format_max_volume(self):
        """
        Returns the volume of the item but formatted properly (i.e. discrete volumes will be formatted as negative floats)
        """
        return self.max_volume if not self.discrete else float(-self.max_volume)

    def as_dict(self):
        """
        Convert fields to dict
        @returns dict with the fields
        """
        return dataclasses.asdict(self)

    def copy(self):
        """
        Creates a copy, nutrition fact is cloned
        """
        return PlateSectionState(nutrition=self.nutrition.copy(),
                                 volume=self.volume,
                                 portion_volume=self.portion_volume,
                                 max_volume=self.max_volume,
                                 section_name=self.section_name,
                                 discrete=self.discrete)

    def with_min_volume(self):
        """
        Clones the state but with the min-volume.
        """
        ret = self.copy()
        ret.volume = ret.min_volume
        return ret

    def with_max_volume(self):
        """
        Clones the state but with the max-volume.
        """
        ret = self.copy()
        ret.volume = ret.max_volume
        return ret

    def with_mid_volume(self):
        """
        Clones the state but with the mid-volume.
        """
        ret = self.copy()
        if ret.discrete:
            ret.volume = ceil_div(3 * ret.max_volume, 4)
        else:
            ret.volume = 0.75 * ret.max_volume
        return ret

    def nudge(self, ratio):
        """
        Updates the volume based on some fraction/ratio of the max volume, making sure to clamp at max/min values, and
        dealing with special cases with discrete values
        @param ratio Ratio to nudge the volume by
        @returns The old volume, pre-nudge
        """
        old_volume = self.volume
        if self.discrete:
            abs_change = int(math.ceil(abs(ratio) * self.max_volume))
            self.volume = clamp(self.volume + abs_change * int((ratio > 0) - (ratio < 0)), self.min_volume, self.max_volume)
        else:
            self.volume = clamp(self.volume + ratio * self.max_volume, self.min_volume, self.max_volume)
        return old_volume


def nutrition_of(state: list[PlateSectionState]):
    res = Nutrition()
    for s in state:
        res += s.scaled_nutrition()
    return res


# Source: https://en.wikipedia.org/wiki/Simulated_annealing#Overview
# https://codeforces.com/blog/entry/94437
# I am peak intuition
class SimulatedAnnealing:
    def __init__(self, profile: StudentProfile, large: list[MealItem], small1: list[MealItem], small2: list[MealItem],
                 large_max_volume: float, small_max_volume: float,
                 alpha: float = 0.999, smallest_temp: float = 0.0005):
        # Info properties
        self.lo_req, self.hi_req = nutritional_info_for(profile)

        # Parameter properties
        self.alpha = alpha
        self.smallest_temp = smallest_temp

        # State properties
        self.t = 1
        self.last_nudge: tuple[int, float] = (0, 0)
        self.state: list[PlateSectionState] = []
        self.item_ids: list[int] = []  # list of meal items corresponding to the item that each state represents
        for items, container_volume, section_name in zip((large, small1, small2),
                                                         (large_max_volume, small_max_volume, small_max_volume),
                                                         ('large', 'small1', 'small2')):
            for item in items:
                self.state.append(PlateSectionState.from_meal_item(item, container_volume, len(items), section_name))
                self.item_ids.append(item.id)

        # Result properties
        self.done = False
        self.final_cost = -1
        self.runtime = -1

    def mid_state(self):
        """
        Returns the middle state
        """
        return [state.with_mid_volume() for state in self.state]

    def lo_state(self):
        """
        Returns the minimum possible state
        """
        return [state.with_min_volume() for state in self.state]

    def hi_state(self):
        """
        Returns the maximum possible state
        """
        return [state.with_max_volume() for state in self.state]

    def nudge(self, t):
        """
        Nudges the current state to a random neighbour based on a given temperature
        """
        idx = random.randint(0, len(self.state) - 1)
        self.last_nudge = idx, self.state[idx].nudge(t * random_sign())

    def un_nudge(self):
        """
        Un-nudges self.state based on the self.last_nudge property (which is set by self.nudge)
        """
        idx, old_volume = self.last_nudge
        self.state[idx].volume = old_volume

    def cost_of(self, state):
        cur_info = nutrition_of(state)
        res = 0

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

    def accept_probability_of(self, c_new: float, c_old: float, scale_coeff: float):
        return 1 if c_new <= c_old else exp(-(c_new - c_old) * scale_coeff / self.t)

    def run_algorithm(self):
        # set RNG
        if settings.PROD:
            random.seed(20210226)

        # Initialization
        cost_bound = max(self.cost_of(self.lo_state()), self.cost_of(self.hi_state()))
        scale_cost_by = 60 / cost_bound
        self.state = self.mid_state()

        # tot=0
        # def volumes():
        #     return [s.volume for s in self.state]
        # print(self.state)

        # Run algorithm
        start_time = time.perf_counter()
        t = 0.5  # Initial Temp, we only take half to full filled anyway
        while t >= self.smallest_temp:

            c_old = self.cost_of(self.state)
            # if tot <= 100: print(f'{t=} {volumes()=}, new_state: ', end='')
            self.nudge(t)
            c_new = self.cost_of(self.state)
            # if tot <= 100: print(f'{volumes()=} {c_old=} {c_new=}')
            # tot+=1
            if self.accept_probability_of(c_new, c_old, scale_cost_by) < random.random():
                self.un_nudge()  # undo the nudge if it failed

            # update tmp
            t *= self.alpha

        # print(nutrition_of(self.state))


        # Set result vars
        self.runtime = time.perf_counter() - start_time
        self.final_cost = self.cost_of(self.state)
        self.done = True

    # Some result properties
    def result_obj(self):
        """
        Returns the result of the algorithm according to the endpoint specifications in the README.md.  The result will
        be in a JSON-serializable format
        """
        return [{
            'id': item_id,
            'volume': state.volume,
            'total_volume': state.max_volume,
            'section': state.section_name
        } for state, item_id in zip(self.state, self.item_ids)]
