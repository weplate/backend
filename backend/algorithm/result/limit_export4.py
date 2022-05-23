import sys
from pathlib import Path
sys.path[0] = str(Path(sys.path[0]).parent.parent)
print(sys.path[0])
import datetime
import pandas as pd
import numpy as np
import os
from dataclasses import fields
from datetime import date
from alive_progress import alive_bar

from backend.algorithm.common import * 
from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import DEFAULT_COEFFICIENTS, PlateSectionState, MealItemSpec, SimulatedAnnealing
from backend.algorithm.requirements import StudentProfileSpec, nutritional_info_for
from backend.algorithm.common import Nutrition

NUTRIENTS = ['calories', 'carbohydrate', 'protein','total_fat','saturated_fat', 'trans_fat',
'sugar', 'cholesterol', 'fiber','sodium', 'potassium', 'calcium','iron', 'vitamin_a', 'vitamin_c', 'vitamin_d']
NUTRITION_TABLE_LATEST = os.path.join(sys.path[0], 'backend_data_parsing/babson/master_nutrition/nutrition_table.csv')
MENU_LATEST= os.path.join(sys.path[0], 'backend_data_parsing/babson/master_menu/menu.csv')
STUDENT = r'C:\Users\Penelope\Desktop\ML\Weplate\synthetic_data\fake_data_may_female.csv'



def retrieve_result(algo_portion_state):
        data_combination = []
        portion_volume = []
        for s in algo_portion_state:
            dish_nutrient = []
            for nutrient in NUTRIENTS:
                dish_nutrient.append(getattr(s.nutrition, nutrient))
            if s.discrete == False:
                dish_nutrient = [dn/s.portion_volume*s.volume for dn in dish_nutrient]
            data_combination.append(dish_nutrient)
            portion_volume.append(s.volume)
        data_combination = np.array(data_combination)
        
        return portion_volume + list(sum(data_combination)) 

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

def get_nutrient_limit(spec):
    n_lo, n_hi = nutritional_info_for(spec)
    return list(zip(nutrition_to_list(n_lo), nutrition_to_list(n_hi)))

if __name__ == '__main__':
    master_nutrition_df = pd.read_csv(NUTRITION_TABLE_LATEST, 
    converters={'cafeteria_id': lambda x: str(x), 'category': lambda x: str(x)})
    master_menu_df = pd.read_csv(MENU_LATEST, 
    converters={'cafeteria_id': lambda x: str(x), 'category': lambda x: str(x)})
    student_df = pd.read_csv(STUDENT)
    student_df['Birthday'] = pd.to_datetime(student_df['Birthday'])
    DATA = []
    for ind_student, student_row in student_df.iterrows():
        print('student-index:', ind_student)
        height = student_row['Height']
        weight = student_row['Weight']
        sex = eval(student_row['Sex'].upper())
        meal_length = 50
        health_goal = eval(student_row['Health_Goal'].upper())
        activity_level = eval(student_row['Activity'].upper())
        yr = student_row['Birthday'].year
        mon = student_row['Birthday'].month
        dat = student_row['Birthday'].day
        birthdate = datetime.date(year=yr, month=mon, day=dat)
        meals = ['breakfast', 'lunch']
        age = 2022 - yr
        
        profile_s = StudentProfileSpec(height=height,weight=weight,
                                        birthdate=birthdate, meals=meals,
                                        meal_length=50,sex=sex,
                                        health_goal=health_goal,
                                        activity_level=activity_level)

        limit_s =  get_nutrient_limit(profile_s)
        protein_limit = limit_s[0]
        carbohydrate_limit = limit_s[1]
        calories_limit = limit_s[2]
        total_fat_limit = limit_s[3]
        saturated_fat_limit = limit_s[4]
        d = [ind_student, protein_limit, carbohydrate_limit, calories_limit, total_fat_limit, saturated_fat_limit]
        DATA.append(d)

    DATA_df =  pd.DataFrame(DATA, columns=['Student_Number','protein_lim', 'carbohydrate_lim', 'calories_limit', 'total_fat_lim', 'saturated_fat_lim'])
    DATA_df.to_csv('nutrient_limit_female.csv', index=False)   

    