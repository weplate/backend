import dataclasses
import math
import random
import time
from dataclasses import dataclass
from math import exp
from typing import Union

from .common import Nutrition


@dataclass
class MealItemSpec:
    id: int
    category: str
    cafeteria_id: str
    portion_volume: float
    max_pieces: int

    calories: float = 0.
    carbohydrate: float = 0.
    protein: float = 0.
    total_fat: float = 0.
    saturated_fat: float = 0.
    trans_fat: float = 0.

    sugar: float = 0.
    cholesterol: float = 0.
    fiber: float = 0.

    sodium: float = 0.
    potassium: float = 0.
    calcium: float = 0.
    iron: float = 0.

    vitamin_a: float = 0.
    vitamin_c: float = 0.
    vitamin_d: float = 0.


def clamp(x: float, a: float, b: float) -> float:
    """
    Clamps a value x within the range [a, b]

    @param x: Value to clamp
    @param a: Lower bound
    @param b: Upper bound
    @return:
    """

    if x < a:
        return a
    elif x > b:
        return b
    return x


def dist_sq(x: float, l: float, r: float) -> float:
    """
    Returns smallest distance (squared) from x to any number in the range [l, r]

    @param x: Point to check distance of (on the number line)
    @param l: Lower bound of the range
    @param r: Upper bound of the range
    @return:
    """
    if x < l:
        return (l - x) ** 2
    elif r < x:
        return (x - r) ** 2
    return 0


def random_sign() -> int:
    """
    Randomly returns -1 or 1
    @return:
    """
    return 1 - 2 * random.randint(0, 1)  # random sign


def ceil_div(a: int, b: int) -> int:
    """
    Given non-negative integers, returns ceil(a / b)

    @param a: self-explanatory
    @param b: self-explanatory
    @return:
    """
    return (a + b - 1) // b


@dataclass
class PlateSectionState:
    nutrition: Nutrition
    portion_volume: Union[float, int]
    discrete: bool
    max_volume: Union[float, int]
    volume: Union[float, int] = 0
    section_name: str = 'n/a'
    id: str = 'n/a'  # We allow string for both the integration (which expects primary keys (ints)) and whatever penelope is doing

    @classmethod
    def from_item_spec(cls, item: MealItemSpec, container_volume: float, num_sections: int, section_name: str):
        """
        Creates a PlateSectionState (with 0 cur. volume) from a given meal item (as MealItemSpec) and other parameters
        @param item The meal item to create the object from
        @param container_volume The total container volume, in DB format (i.e. positive for continuous, negative integer for discrete)
        @param num_sections The number of sections this container is divided into (so the actual volume can be computed by how much of the section this occupies)
        @param section_name The name of the section (currently, "large", "small1", or "small2")
        @return A PlateSectionState object
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

        return PlateSectionState(nutrition=Nutrition.from_object(item),
                                 portion_volume=portion_volume,
                                 discrete=discrete,
                                 max_volume=max_volume,
                                 volume=volume,
                                 section_name=section_name,
                                 id=str(item.id))

    @property
    def min_volume(self):
        """
        @return: Returns the min volume instead of the max volume
        """
        return max(1, ceil_div(self.max_volume, 2)) if self.discrete else self.max_volume / 2

    def scaled_nutrition(self):
        """
        @return: Returns the nutrition facts scaled by the portion volume
        """
        return self.nutrition * (self.volume / self.portion_volume)

    def format_volume(self):
        """
        @return: Returns the volume of the item but formatted properly (i.e. discrete volumes are negative
        """
        return self.volume if not self.discrete else float(-self.volume)

    def format_max_volume(self):
        """
        @return: Returns the volume of the item but formatted properly (i.e. discrete volumes will be formatted as negative floats)
        """
        return self.max_volume if not self.discrete else float(-self.max_volume)

    def as_dict(self):
        """
        Convert fields to dict
        @return: dict with the fields
        """
        return dataclasses.asdict(self)

    def copy(self):
        """
        @return: Creates a copy, nutrition facts are cloned recursively
        """
        return PlateSectionState(nutrition=self.nutrition.copy(),
                                 volume=self.volume,
                                 portion_volume=self.portion_volume,
                                 max_volume=self.max_volume,
                                 section_name=self.section_name,
                                 discrete=self.discrete,
                                 id=self.id)

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
        @return: The old volume, pre-nudge
        """
        old_volume = self.volume
        if self.discrete:
            abs_change = int(math.ceil(abs(ratio) * self.max_volume))
            self.volume = clamp(self.volume + abs_change * int((ratio > 0) - (ratio < 0)), self.min_volume,
                                self.max_volume)
        else:
            self.volume = clamp(self.volume + ratio * self.max_volume, self.min_volume, self.max_volume)
        return old_volume


def nutrition_of(state: list[PlateSectionState]):
    """
    Given a list of PlateSectionStates, sums the scaled nutrition facts over the states
    @param state:
    @return: The summed nutrition facts over all states
    """
    res = Nutrition()
    for s in state:
        res += s.scaled_nutrition()
    return res


# Source: https://en.wikipedia.org/wiki/Simulated_annealing#Overview
# https://codeforces.com/blog/entry/94437
# I am peak intuition
class SimulatedAnnealing:
    def __init__(self, lo_req: Nutrition, hi_req: Nutrition, state: list[PlateSectionState],
                 alpha: float, smallest_temp: float, seed: int):
        """
        Creates a SimulatedAnnealing object which can run the portion-selecting algorithm
        @param lo_req: Nutritional minimums.  Treat |x| > 1e10 as INF
        @param hi_req: Nutritional maximums.  Treat |x| > 1e10 as INF
        @param state: Initial algorithm state, as a list of PlateSectionState.  For the purposes of data analysis of
        algorithm performance, each element can be constructed using the first four parameters with the rest being in
        their default state.
        @param alpha: Optional. Amount temperature is multiplied by after each iteration
        @param smallest_temp: Optional. Minimal temperature before algorithm termination.
        @param seed: Optional.  Seed value of RNG to make run deterministic.  -1 means no set seed
        """
        # Info properties
        self.lo_req = lo_req
        self.hi_req = hi_req

        # Parameter properties
        self.seed = seed
        self.alpha = alpha
        self.smallest_temp = smallest_temp

        # State properties
        self.t = 1
        self.last_nudge: tuple[int, float] = (0, 0)
        self.state: list[PlateSectionState] = state

        # Result properties
        self.done = False
        self.final_cost = -1
        self.runtime = -1

    def mid_state(self):
        """
        @return: Copies the current state except state[i].volume is at the middle value
        """
        return [state.with_mid_volume() for state in self.state]

    def lo_state(self):
        """
        @return: Copies the current state except state[i].volume is at the min value
        """
        return [state.with_min_volume() for state in self.state]

    def hi_state(self):
        """
        @return: Copies the current state except state[i].volume is at the max value
        """
        return [state.with_max_volume() for state in self.state]

    def nudge(self, t):
        """
        Nudges self.state to a random neighbour based on a given temperature
        @return: None
        """
        idx = random.randint(0, len(self.state) - 1)
        self.last_nudge = idx, self.state[idx].nudge(t * random_sign())

    def un_nudge(self):
        """
        Un-nudges self.state based on the self.last_nudge property (which is set by self.nudge(...))
        @return: None
        """
        idx, old_volume = self.last_nudge
        self.state[idx].volume = old_volume

    def cost_of(self, state):
        """
        Given a state, returns its cost, which is based on the current nutritional limits (upper and lower).
        @param state: Self-explanatory
        @return: Self-explanatory
        """
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
        """
        Computes the acceptance probability of a new state given the costs of the old and new state.  See
        https://en.wikipedia.org/wiki/Simulated_annealing
        @param c_new: Cost of the new state
        @param c_old: Cost of the old state
        @param scale_coeff: Coefficient to scale the cost difference by when computing acceptance probability.
        @return: Self-explanatory
        """
        return 1 if c_new <= c_old else exp(-(c_new - c_old) * scale_coeff / self.t)

    def run_algorithm(self):
        """
        Runs the algorithm
        @return: None, the result of the algorithm will be stored in the final state (self.state).  You can use
        backend.algorithm.integration to retrieve the result in a way that will be returned to the frontend.
        """
        if self.seed != -1:
            random.seed(self.seed)

        # Initialization
        cost_bound = max(self.cost_of(self.lo_state()), self.cost_of(self.hi_state()))
        scale_cost_by = 60 / cost_bound
        self.state = self.mid_state()

        # Run algorithm
        start_time = time.perf_counter()
        t = 0.5  # Initial Temp, we only take half to full filled anyway
        while t >= self.smallest_temp:

            c_old = self.cost_of(self.state)
            self.nudge(t)
            c_new = self.cost_of(self.state)
            if self.accept_probability_of(c_new, c_old, scale_cost_by) < random.random():
                self.un_nudge()  # undo the nudge if it failed

            # update tmp
            t *= self.alpha

        # Set result vars
        self.runtime = time.perf_counter() - start_time
        self.final_cost = self.cost_of(self.state)
        self.done = True
