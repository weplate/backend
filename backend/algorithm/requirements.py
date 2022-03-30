import datetime

from backend.algorithm.common import Nutrition
from backend.models import StudentProfile

# JSON does not support infinity
INF = 10**20

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#a976edca5f394d26b536704ff6f691ce
DEFAULT_LO_REQS = dict(
    # Macro
    calories=-1,  # closest
    carbohydrate=-1,  # closest
    protein=-1,  # closest
    total_fat=-1,  # closest
    saturated_fat=-1,  # closest
    trans_fat=0,  # closest

    # Micro
    sugar=-INF,  # at most
    cholesterol=-INF,  # at most
    fiber=30,  # at least
    sodium=1500,  # range
    potassium=3000,  # at least
    calcium=1000,  # at least
    iron=8,  # at least
    vitamin_d=600,  # at least
    vitamin_c=90,  # at least
    vitamin_a=3000,  # at least
)

DEFAULT_HI_REQS = dict(
    # Macro
    calories=-1,  # closest
    carbohydrate=-1,  # closest
    protein=-1,  # closest
    total_fat=-1,  # closest
    saturated_fat=-1,  # closest
    trans_fat=0,  # closest

    # Micro
    sugar=27,  # at most
    cholesterol=300,  # at most
    fiber=INF,  # at least
    sodium=4000,  # at most
    potassium=INF,  # at least
    calcium=2500,  # at least
    iron=45,  # at least
    vitamin_d=4000,  # at least
    vitamin_c=2000,  # at least
    vitamin_a=10000,  # at least
)

# Calorie coefficients
ACTIVITY_LEVEL_COEFF = {
    StudentProfile.SEDENTARY: 1.2,
    StudentProfile.MILD: 1.3,
    StudentProfile.MODERATE: 1.5,
    StudentProfile.HEAVY: 1.7,
    StudentProfile.EXTREME: 1.9,
}

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#a976edca5f394d26b536704ff6f691ce
# Base, Weight, Height, Age
SEX_COEFF = {  # 69
    StudentProfile.MALE: (88.362, 13.397, 4.799, 5.677),
    StudentProfile.FEMALE: (447.593, 9.247, 3.098, 4.330)
}

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#72d92545467d40faa8508132432618c8
# Protein, Carb, Fat, Saturated Fat - Each item is a tuple (lo, hi)
# For protein and carb, the % are based on body weight
# For fat and saturated fat, the % are based on total caloric intake (/9 as fat is 9 cal/g)
MACROS_COEFF = {
    StudentProfile.BUILD_MUSCLE: ((1.5, 1.8), (6, 6.6), (0.3, 0.35), (0, 0.1)),
    StudentProfile.ATHLETIC_PERFORMANCE: ((0.9, 1.05), (6, 6.6), (0.3, 0.35), (0, 0.1)),
    StudentProfile.LOSE_WEIGHT: ((1.1, 1.3), (5, 5.5), (0.2, 0.25), (0, 0.1)),
    StudentProfile.IMPROVE_TONE: ((0.8, 1), (6, 6.3), (0.25, 0.3), (0, 0.1)),
    StudentProfile.IMPROVE_HEALTH: ((0.8, 1), (5, 6), (0.2, 0.25), (0, 0.1))
}

# https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea#422b95b3b18c47dbbbee6eec642ee779
# Max portion sizes and min fill requirement, in ML
CALS_IN_FAT = 9
SMALL_PORTION_MAX = 270
LARGE_PORTION_MAX = 610
MIN_FILL = 0.5


def nutritional_info_for(profile: StudentProfile) -> tuple[Nutrition, Nutrition]:
    for req_prop in ('activity_level', 'sex', 'weight', 'height', 'birthdate'):
        if not hasattr(profile, req_prop):
            raise ValueError(f'Student profile missing attribute {req_prop}')

    # Formulae: https://www.notion.so/weplate/Mathematical-Calculations-f561b494f2444cfc87023ef615cf2bea:w
    c_base, c_weight, c_height, c_age = SEX_COEFF[profile.sex]
    c_activity = ACTIVITY_LEVEL_COEFF[profile.activity_level]
    age = (datetime.date.today() - profile.birthdate).days // 365  # Leap years are fake news
    lo = Nutrition(**DEFAULT_LO_REQS)
    hi = Nutrition(**DEFAULT_HI_REQS)

    # Set calorie count
    calories = (c_base + c_weight * profile.weight + c_height * profile.height - c_age * age) * c_activity * 1.1
    if profile.health_goal == StudentProfile.LOSE_WEIGHT:
        calories -= 250
    elif profile.health_goal == StudentProfile.BUILD_MUSCLE:
        calories += 250
    lo.calories = calories * 0.85  # Have some leeway
    hi.calories = calories * 1.15

    # Set Macros count
    protein, carb, fat, sat_fat = MACROS_COEFF[profile.health_goal]
    lo.protein = protein[0] * profile.weight
    hi.protein = protein[1] * profile.weight
    lo.carbohydrate = carb[0] * profile.weight
    hi.carbohydrate = carb[1] * profile.weight
    lo.total_fat = fat[0] * calories / CALS_IN_FAT  # Use exact calorie requirements
    hi.total_fat = fat[1] * calories / CALS_IN_FAT

    # Divide reqs by 3 since these are daily
    for prop in DEFAULT_HI_REQS.keys():  # Doesn't matter if hi or lo
        setattr(lo, prop, getattr(lo, prop) / 3)
        setattr(hi, prop, getattr(hi, prop) / 3)

    return lo, hi
