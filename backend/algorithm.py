import datetime
import random

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
    reqs.total_fat = fat_cal_ratio * reqs.calories
    reqs.saturated_fat = sat_fat_cal_ratio * reqs.calories
    reqs.sugar = SUGAR_REQS[profile.sex]

    # Divide reqs by 3 since these are daily
    for prop in DEFAULT_REQS.keys():
        if prop != 'name':  # gotta remove this one!
            setattr(reqs, prop, getattr(reqs, prop) / 3)

    return reqs


def classify_item(item: MealItem):
    pass


# Source: https://en.wikipedia.org/wiki/Simulated_annealing#Overview
def simulated_annealing(big_item: MealItem, small_item_1: MealItem, small_item_2: MealItem,
                        requirements: NutritionalInfo, iterations: int):
    state = NutritionalInfo()

    def temperature(k):
        pass

    def neighbour(state, T):
        pass

    def cost(state):
        pass

    def accept_probability(state_new, state_old, T):
        pass

    for k in range(iterations):
        T = temperature(1 - (k + 1) / iterations)
        state_new = neighbour(state, T)
        if accept_probability(state_new, state, T) >= random.random():
            state = state_new

    return state
