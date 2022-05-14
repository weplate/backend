import sys
from pathlib import Path
sys.path[0] = str(Path(sys.path[0]).parent.parent)

from backend.algorithm.common import Nutrition
from backend.algorithm.requirements import nutritional_info_for, StudentProfileSpec
from datetime import date, timedelta

def nutrition_to_list(nut: Nutrition):
    return [nut.protein,
            nut.carbohydrate,
            nut.calories,
            nut.total_fat,
            nut.saturated_fat,
            nut.sodium,
            nut.calcium,
            nut.iron,
            nut.vitamin_a,
            nut.vitamin_c,
            nut.vitamin_d,
            nut.sugar,
            nut.cholesterol,
            nut.fiber,
            nut.potassium]


def get_nutrient_limit_new(spec):
    n_lo, n_hi = nutritional_info_for(spec)
    return list(zip(nutrition_to_list(n_lo), nutrition_to_list(n_hi)))

if __name__ == '__main__':
    profile = StudentProfileSpec(height=170, weight=70, birthdate=date.today() - timedelta(days=18 * 365), meals=[], meal_length = -1, sex='male', health_goal='build_muscle', activity_level='moderate')
    ln = get_nutrient_limit_new(profile)

    for ll in ln:
        print(ll[0])
    


