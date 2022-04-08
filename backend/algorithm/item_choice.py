import itertools
import time

from backend.algorithm.portion import SimulatedAnnealing
from backend.algorithm.requirements import nutritional_info_for
from backend.models import MealSelection, StudentProfile, MealItem


class PlateSection:
    LARGE = 'large'
    SMALL1 = 'small1'
    SMALL2 = 'small2'

    @classmethod
    def all(cls):
        return [cls.LARGE, cls.SMALL1, cls.SMALL2]


# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#c137e967c1224678be2079cb5a55a3a6
# Which section (protein, veg, carb) should have the large portion
LARGE_PORTION = {
    StudentProfile.BUILD_MUSCLE: MealItem.PROTEIN,
    StudentProfile.ATHLETIC_PERFORMANCE: MealItem.GRAINS,
    StudentProfile.LOSE_WEIGHT: MealItem.VEGETABLE,
    StudentProfile.IMPROVE_TONE: MealItem.PROTEIN,
    StudentProfile.IMPROVE_HEALTH: MealItem.VEGETABLE
}

# How many items to pick
CHOOSE_COUNT = 3


class MealItemSelector:
    def __init__(self, meal: MealSelection, profile: StudentProfile,
                 large_portion_max: float, small_portion_max: float,
                 sa_alpha: float = 0.99, sa_lo: float = 0.01):
        self.meal = meal
        self.profile = profile
        self.sa_alpha = sa_alpha
        self.sa_lo = sa_lo
        self.large_portion_max = large_portion_max
        self.small_portion_max = small_portion_max

        self.requirements = nutritional_info_for(profile)
        self._result_obj = {}
        self.result_cost = -1
        self.runtime = -1
        self.done = False

    def run_algorithm(self):
        large_items = self.meal.items.filter(category=MealItem.PROTEIN)
        small1_items = self.meal.items.filter(category=MealItem.VEGETABLE)
        small2_items = self.meal.items.filter(category=MealItem.GRAINS)
        large_category = MealItem.PROTEIN
        small1_category = MealItem.VEGETABLE
        small2_category = MealItem.GRAINS

        if LARGE_PORTION[self.profile.health_goal] == MealItem.VEGETABLE:
            large_items, small1_items = small1_items, large_items
            large_category, small1_category = small1_category, large_category
        elif LARGE_PORTION[self.profile.health_goal] == MealItem.GRAINS:
            large_items, small2_items = small2_items, large_items
            large_category, small2_category = small2_category, large_category

        cost_cache = {}
        start_time = time.perf_counter()

        def cache_id(item_1, item_2, item_3):
            return f'{item_1.pk}-{item_2.pk}-{item_3.pk}'

        for item_l, item_s1, item_s2 in itertools.product(large_items.all(), small1_items.all(), small2_items.all()):
            sa = SimulatedAnnealing(self.profile, [item_l], [item_s1], [item_s2], self.large_portion_max,
                                    self.small_portion_max, self.sa_alpha, self.sa_lo)
            sa.run_algorithm()
            cost_cache[cache_id(item_l, item_s1, item_s2)] = sa.final_cost

        best = ([], [], [])
        best_cost = sum(cost_cache.values()) + 1
        for comb_l, comb_s1, comb_s2 in itertools.product(
                itertools.combinations(large_items.all(), min(CHOOSE_COUNT, large_items.count())),
                itertools.combinations(small1_items.all(), min(CHOOSE_COUNT, small1_items.count())),
                itertools.combinations(small2_items.all(), min(CHOOSE_COUNT, small2_items.count()))
        ):
            l1 = list(comb_l)
            l2 = list(comb_s1)
            l3 = list(comb_s2)
            cur_cost = 0
            for x, y, z in itertools.product(l1, l2, l3):
                cur_cost += cost_cache[cache_id(x, y, z)]

            if cur_cost < best_cost:
                best_cost = cur_cost
                best = (l1, l2, l3)

        def to_pk_list(items):
            return [item.pk for item in items]

        l1, l2, l3 = best
        self._result_obj = {
            PlateSection.LARGE: {
                'items': to_pk_list(l1),
                'category': large_category
            },
            PlateSection.SMALL1: {
                'items': to_pk_list(l2),
                'category': small1_category
            },
            PlateSection.SMALL2: {
                'items': to_pk_list(l3),
                'category': small2_category
            },
        }
        self.result_cost = best_cost
        self.runtime = time.perf_counter() - start_time
        self.done = True

    def result_obj(self):
        return self._result_obj
