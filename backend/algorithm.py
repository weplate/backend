import datetime
import random
import time
from math import exp

from backend.models import NutritionalInfo, StudentProfile, MealItem

DEFAULT_REQS = dict(
    name='Nutritional Requirements',
    # Macro
    calories=0,
    carbohydrate=0,
    protein=0,
    total_fat=0,
    saturated_fat=0,
    trans_fat=0,

    # Micro
    sugar=0,
    cholesterol=0,
    fiber=4,
    sodium=620,
    potassium=240,
    calcium=470,
    iron=3,
    vitamin_d=0,
    vitamin_c=16,
    vitamin_a=0,
)

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#a976edca5f394d26b536704ff6f691ce
ACTIVITY_LEVEL_COEFF = {
    StudentProfile.MILD: 1.3,
    StudentProfile.MODERATE: 1.5,
    StudentProfile.HEAVY: 1.7,
    StudentProfile.EXTREME: 1.9
}

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#a976edca5f394d26b536704ff6f691ce
# Base, Weight, Height, Age
SEX_COEFF = {  # 69
    StudentProfile.MALE: (88.362, 13.397, 4.799, 5.677),
    StudentProfile.FEMALE: (447.593, 9.247, 3.098, 4.330)
}

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#72d92545467d40faa8508132432618c8
# Protein, Carb, Fat, Saturated Fat
MACROS_COEFF = {
    StudentProfile.BUILD_MUSCLE: (1.6, (6 + 6.6) / 2, (0.3 + 0.35) / 2, 0.1),
    StudentProfile.ATHLETIC_PERFORMANCE: (1, (6 + 6.6) / 2, 0.3, 0.1),  # Protein: upper range recommended
    StudentProfile.LOSE_WEIGHT: ((0.8 + 1) / 2, 5, (0.2 + 0.25) / 2, 0.1),
    StudentProfile.IMPROVE_TONE: ((0.8 + 1) / 2, 6, (0.25 + 0.3) / 2, 0.1),
    StudentProfile.IMPROVE_HEALTH: ((0.8 + 1) / 2, 5, (0.2 + 0.25) / 2, 0.1)
}

CALS_IN_FAT = 9

SUGAR_REQS = {
    StudentProfile.MALE: 36,
    StudentProfile.FEMALE: 25
}

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#422b95b3b18c47dbbbee6eec642ee779
# Max portion sizes and min fill requirement, in ML
SMALL_PORTION_MAX = 270
LARGE_PORTION_MAX = 610
MIN_FILL = 0.5


# More Stuff
class ItemType:
    PROTEIN = 'protein'
    VEGETABLE = 'vegetable'
    CARBOHYDRATE = 'carbohydrate'


# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#c137e967c1224678be2079cb5a55a3a6
# Which section (protein, veg, carb) should have the large portion
LARGE_PORTION = {
    StudentProfile.BUILD_MUSCLE: ItemType.PROTEIN,
    StudentProfile.ATHLETIC_PERFORMANCE: ItemType.CARBOHYDRATE,
    StudentProfile.LOSE_WEIGHT: ItemType.VEGETABLE,
    StudentProfile.IMPROVE_TONE: ItemType.PROTEIN,
    StudentProfile.IMPROVE_HEALTH: ItemType.VEGETABLE
}


def nutritional_info_for(profile: StudentProfile) -> NutritionalInfo:
    for req_prop in ('activity_level', 'sex', 'weight', 'height', 'birthdate'):
        if not hasattr(profile, req_prop):
            raise ValueError(f'Student profile missing attribute {req_prop}')

    # Formulae: https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea:w
    c_base, c_weight, c_height, c_age = SEX_COEFF[profile.sex]
    c_activity = ACTIVITY_LEVEL_COEFF[profile.activity_level]
    age = (datetime.date.today() - profile.birthdate).days // 365  # Leap years are fake news
    reqs = NutritionalInfo(**DEFAULT_REQS)

    # Set calorie count
    reqs.calories = (c_base + c_weight * profile.weight + c_height * profile.height - c_age * age) * c_activity * 1.1
    if profile.health_goal == StudentProfile.LOSE_WEIGHT:
        reqs.calories -= 250
    elif profile.health_goal == StudentProfile.BUILD_MUSCLE:
        reqs.calories += 250

    # Set Macros count
    protein_ratio, carb_ratio, fat_cal_ratio, sat_fat_cal_ratio = MACROS_COEFF[profile.health_goal]
    reqs.protein = protein_ratio * profile.weight
    reqs.carbohydrate = carb_ratio * profile.weight
    reqs.total_fat = fat_cal_ratio * reqs.calories / CALS_IN_FAT
    reqs.saturated_fat = sat_fat_cal_ratio * reqs.calories / CALS_IN_FAT
    reqs.sugar = SUGAR_REQS[profile.sex]

    # Divide reqs by 3 since these are daily
    for prop in DEFAULT_REQS.keys():
        if prop != 'name':  # gotta remove this one!
            setattr(reqs, prop, getattr(reqs, prop) / 3)

    return reqs


def classify_item(item: MealItem):
    pass


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


def fast_combine(m1: MealItem, m2: MealItem, m3: MealItem, c1, c2, c3):
    """
    Sums the nutritional information of three meal items together when given portion sizes (in mL).  Dicts are slow
    so we're doing this manually

    @param m1 First meal item
    @param m2 Second meal item
    @param m3 Third meal item
    @param c1 Volume of first meal item
    @param c2 Volume of second meal item
    @param c3 Volume of third meal item
    """

    n1 = m1.nutrition
    n2 = m2.nutrition
    n3 = m3.nutrition
    res = NutritionalInfo()
    s1 = c1 / m1.portion_volume
    s2 = c2 / m2.portion_volume
    s3 = c3 / m3.portion_volume

    res.calories = n1.calories * s1 + n2.calories * s2 + n3.calories * s3
    res.carbohydrate = n1.carbohydrate * s1 + n2.carbohydrate * s2 + n3.carbohydrate * s3
    res.protein = n1.protein * s1 + n2.protein * s2 + n3.protein * s3
    res.total_fat = n1.total_fat * s1 + n2.total_fat * s2 + n3.total_fat * s3
    res.saturated_fat = n1.saturated_fat * s1 + n2.saturated_fat * s2 + n3.saturated_fat * s3
    res.trans_fat = n1.trans_fat * s1 + n2.trans_fat * s2 + n3.trans_fat * s3

    res.sugar = n1.sugar * s1 + n2.sugar * s2 + n3.sugar * s3
    res.cholesterol = n1.cholesterol * s1 + n2.cholesterol * s2 + n3.cholesterol * s3
    res.fiber = n1.fiber * s1 + n2.fiber * s2 + n3.fiber * s3
    res.sodium = n1.sodium * s1 + n2.sodium * s2 + n3.sodium * s3
    res.potassium = n1.potassium * s1 + n2.potassium * s2 + n3.potassium * s3
    res.calcium = n1.calcium * s1 + n2.calcium * s2 + n3.calcium * s3
    res.iron = n1.iron * s1 + n2.iron * s2 + n3.iron * s3

    res.vitamin_d = n1.vitamin_d * s1 + n2.vitamin_d * s2 + n3.vitamin_d * s3
    res.vitamin_c = n1.vitamin_c * s1 + n2.vitamin_c * s2 + n3.vitamin_c * s3
    res.vitamin_a = n1.vitamin_a * s1 + n2.vitamin_a * s2 + n3.vitamin_a * s3

    return res


# Source: https://en.wikipedia.org/wiki/Simulated_annealing#Overview
# https://codeforces.com/blog/entry/94437

def simulated_annealing(big_item: MealItem, small_item_1: MealItem, small_item_2: MealItem,
                        requirements: NutritionalInfo, iterations: int = 10000, alpha: float = 0.999):
    state = (LARGE_PORTION_MAX * 0.75, SMALL_PORTION_MAX * 0.75, SMALL_PORTION_MAX * 0.75)

    def init_temp():
        return 1

    def temperature(_, cur_t):
        return cur_t * alpha

    def neighbour(cur_state, cur_t):
        l, s1, s2 = cur_state
        rnd = random.randint(0, 2)
        if rnd == 0:
            return move_value(l, cur_t, LARGE_PORTION_MAX / 2, LARGE_PORTION_MAX), s1, s2
        elif rnd == 1:
            return l, move_value(s1, cur_t, SMALL_PORTION_MAX / 2, SMALL_PORTION_MAX), s2
        else:
            return l, s1, move_value(s2, cur_t, SMALL_PORTION_MAX / 2, SMALL_PORTION_MAX)

    def cost(cur_state):
        cur_info = fast_combine(big_item, small_item_1, small_item_2, cur_state[0], cur_state[1], cur_state[2])
        res = 0

        # For macros, the weights are (generally) the amount of calories in each item
        res += (cur_info.calories - requirements.calories) ** 2
        res += 4 * (cur_info.calories - requirements.calories) ** 2
        res += 4 * (cur_info.protein - requirements.protein) ** 2
        res += 9 * (cur_info.total_fat - requirements.total_fat) ** 2
        res += 1.2 * 9 * (cur_info.saturated_fat - requirements.saturated_fat) ** 2
        res += 9 * (cur_info.trans_fat - requirements.trans_fat) ** 2

        # For the rest... I'm kinda just yoloing this ngl...
        res += 3 * (cur_info.sugar - requirements.sugar) ** 2
        res += 0.1 * (cur_info.cholesterol - requirements.cholesterol)
        res += 4 * (cur_info.fiber - requirements.fiber)
        res += 0.2 * (cur_info.sodium - requirements.sodium)
        res += 0.1 * (cur_info.potassium - requirements.potassium)
        res += 0.15 * (cur_info.calcium - requirements.calcium)
        res += 0.5 * (cur_info.iron - requirements.iron)

        # Vitamins!!!
        res += 0.1 * max(0., requirements.vitamin_c - cur_info.vitamin_c) ** 2
        res += 0.1 * max(0., requirements.vitamin_d - cur_info.vitamin_d) ** 2
        res += 0.1 * max(0., requirements.vitamin_a - cur_info.vitamin_a) ** 2

        return res

    def accept_probability(next_state, cur_state, cur_t):
        c_new = cost(next_state)
        c_old = cost(cur_state)
        return 1 if c_new <= c_old else exp(-(c_new - c_old) / cur_t)

    start_time = time.perf_counter()
    t = init_temp()
    for k in range(iterations):
        t = temperature(k, t)
        state_new = neighbour(state, t)
        if accept_probability(state_new, state, t) >= random.random():
            state = state_new

    return state, cost(state), time.perf_counter() - start_time
