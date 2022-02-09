import datetime

from backend.models import NutritionalInfo, StudentProfile

DEFAULT_REQS = dict(
    name='Nutritional Requirements',
    # Macro
    calories=0,
    carbohydrate=0,
    protein=0,
    trans_fat=0,
    saturated_fat=0,
    unsaturated_fat=0,

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


ACTIVITY_LEVEL_COEFF = {
    StudentProfile.MILD: 1.3,
    StudentProfile.MODERATE: 1.5,
    StudentProfile.HEAVY: 1.7,
    StudentProfile.EXTREME: 1.9
}

SEX_COEFF = {
    StudentProfile.MALE: (88.362, 13.397, 4.799, 5.677),
    StudentProfile.FEMALE: (447.593, 9.247, 3.098, 4.330)
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
    reqs.calories = (c_base + c_weight * profile.weight + c_height * profile.height - c_age * age) * c_activity * 1.1

    if profile.health_goal == StudentProfile.LOSE_WEIGHT:
        reqs.calories -= 250
    elif profile.health_goal == StudentProfile.BUILD_MUSCLE:
        reqs.calories += 250

    return reqs
