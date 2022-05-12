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

def get_nutrient_limit(weight, age, sex, height, health_goal, activity_level):
    spec = StudentProfileSpec(height=height,
                              weight=weight,
                              birthdate=date.today() - timedelta(days=age * 365),
                              meals=[],
                              meal_length=-1,
                              sex=sex,
                              health_goal=health_goal,
                              activity_level=activity_level)
    n_lo, n_hi = nutritional_info_for(spec)

    return list(zip(nutrition_to_list(n_lo), nutrition_to_list(n_hi)))

if __name__ == '__main__':
    l = get_nutrient_limit(70, 18, 'male', 178, 'build_muscle', 'moderate')
    for a, b in l:
        print(a, b)
