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

from backend.algorithm.common import * 
from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing, PlateSectionState, MealItemSpec
from backend.algorithm.requirements import StudentProfileSpec, nutritional_info_for

NUTRIENTS = ['calories', 'carbohydrate', 'protein','total_fat','saturated_fat', 'trans_fat',
'sugar', 'cholesterol', 'fiber','sodium', 'potassium', 'calcium','iron', 'vitamin_a', 'vitamin_c', 'vitamin_d']
NUTRITION_TABLE_LATEST = os.path.join(sys.path[0], 'backend_data_parsing/babson/master_nutrition/nutrition_table.csv')
MENU_LATEST= os.path.join(sys.path[0], 'backend_data_parsing/babson/master_menu/old_file/menu.csv')
STUDENT = r'C:\Users\Penelope\Desktop\ML\Weplate\synthetic_data\fake_data_male_apr13_31.csv'

def item_choice_example(height, weight, birthdate, meals, meal_length, sex, health_goal, activity_level, meal_items):
    profile = StudentProfileSpec(height=height,weight=weight,birthdate=birthdate,
    meals=meals,meal_length=50,sex=sex,health_goal=health_goal,activity_level=activity_level)

    algo = MealItemSelector(
        profile=profile,
        items= meal_items,
        large_portion_max=610,
        small_portion_max=270,
        sa_alpha=0.99,
        sa_lo=0.01,
        seed=69696969
    )
    algo.run_algorithm()
    algo.result_obj()  # Check this for result
    return algo.result_obj()


def item_portion_example_old(height):#, weight, birthdate, meals, meal_lenth, sex, health_goal, activity_level):
    profile = StudentProfileSpec(
        height=height,
        weight=80,
        birthdate=datetime.date(year=2003, month=11, day=30),
        meals=['breakfast', 'lunch'],
        meal_length=50,
        sex='male',
        health_goal='athletic_performance',
        activity_level='moderate'
    )

    lo_req, hi_req = nutritional_info_for(profile)

    example_item = MealItemSpec(
        id=1019,
        category='protein',
        cafeteria_id='123456.789',
        portion_volume=-2,  # item is discrete
        max_pieces=15,
        calories=0,
        carbohydrate=0,
        protein=0,
        total_fat=0,
        saturated_fat=0,
        trans_fat=0,
        sugar=0,
        cholesterol=0,
        fiber=0,
        sodium=0,
        potassium=0,
        calcium=0,
        iron=0,
        vitamin_a=0,
        vitamin_c=0,
        vitamin_d=0,
    )

    algo = SimulatedAnnealing(
        lo_req=lo_req,
        hi_req=hi_req,
        state=[
            #platesectionstate can be initialized directly, or
            PlateSectionState(
                nutrition=Nutrition(
                    # nutrition facts
                ),
                portion_volume=100,
                discrete=False,
                max_volume=610,
                id='your mom'
            ),
            PlateSectionState(
                nutrition=Nutrition(
                    # nutrition facts
                ),
                portion_volume=5,  # Number of pieces in a portion
                discrete=True,
                max_volume=10,  # Max num. of pieces
                id='penelopeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            ),
            # done using the helper function
            # Below is an example assuming we had the 'default' weplate plate configuration.
            # ofc use more than one item :p
            PlateSectionState.from_item_spec(example_item,
                                             container_volume=610,  # Volume of the section of the container
                                             num_sections=1,  # Number of items with the given section name, used to calculate the true max volume
                                             section_name='large'),
            PlateSectionState.from_item_spec(example_item,
                                             container_volume=270,
                                             num_sections=1,
                                             section_name='small1'),
            PlateSectionState.from_item_spec(example_item,
                                             container_volume=270,
                                             num_sections=1,
                                             section_name='small2')
        ],
        alpha=0.999,
        smallest_temp=0.0005,
        seed=20210101
    )
    algo.run_algorithm()

    # Final results are in algo.state
    for state in algo.state:
        pass  # final volume is in state.volume, item id is in state.id.  Use state.discrete to check if the item is discrete or not
    return algo.state


def item_portion_example(height, weight, birthdate, meals, meal_length, sex, health_goal, activity_level, state):
    profile = StudentProfileSpec(height=height,weight=weight,birthdate=birthdate,
    meals=meals,meal_length=meal_length,sex=sex,health_goal=health_goal,activity_level=activity_level)
    lo_req, hi_req = nutritional_info_for(profile)
    algo = SimulatedAnnealing(
        lo_req=lo_req,
        hi_req=hi_req,
        state=state,
        alpha=0.999,
        smallest_temp=0.0005,
        seed=20210101
    )
    algo.run_algorithm()

    # Final results are in algo.state
    for state in algo.state:
        pass  # final volume is in state.volume, item id is in state.id.  Use state.discrete to check if the item is discrete or not
    return algo.state

def retrieve_result(algo_portion_state):
        data_combination = []
        portion_volume = []
        for s in algo_portion_state:
            dish_nutrient = []
            for nutrient in NUTRIENTS:
                dish_nutrient.append(getattr(s.nutrition, nutrient))
            data_combination.append(dish_nutrient)
            portion_volume.append(s.volume)
        data_combination = np.array(data_combination)
        
        return portion_volume + list(sum(data_combination)) 

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
        sex = eval(student_row['Sex'])
        meal_length = 50
        health_goal = eval(student_row['Health_Goal'].upper())
        activity_level = eval(student_row['Activity'].upper())
        yr = student_row['Birthday'].year
        mon = student_row['Birthday'].month
        dat = student_row['Birthday'].day
        birthdate = datetime.date(year=yr, month=mon, day=dat)
        meals = ['breakfast', 'lunch']
        age = 2022 - yr
        
        for ind, menu_row in master_menu_df.iterrows():
            day = menu_row['timestamp']
            meal_name = menu_row['name']
            menu = eval(menu_row['items']) #pk
        #menu = [1047, 1021, 1014, 1036, 1037, 1056, 1040]
            if len(menu) > 0:
                meal_items = []
                short_df = pd.DataFrame()
                short_list_df = master_nutrition_df[master_nutrition_df['pk'].isin(menu)]
                for ind, row in short_list_df.iterrows():
                    id = row['pk']
                    cafeteria_id= row['cafeteria_id']
                    category = row['category']
                    portion_volume = float(row['portion_volume'])
                    max_pieces = row['max_pieces']
                    carbohydrate = float(row['carbohydrate'])
                    calories = float(row['calories'])
                    protein = float(row['protein'])
                    total_fat = float(row['total_fat'])
                    saturated_fat = float(row['saturated_fat'])
                    sugar= float(row['sugar'])
                    cholesterol=float(row['cholesterol'])
                    fiber= float(row['fiber'])
                    sodium=float(row['sodium'])
                    potassium=float(row['potassium'])
                    calcium=float(row['calcium'])
                    iron=float(row['iron'])
                    vitamin_a=float(row['vitamin_a'])
                    vitamin_c=float(row['vitamin_c'])
                    vitamin_d=float(row['vitamin_d'])

                    meal_items.append(MealItemSpec(id=id, category=category, portion_volume=portion_volume,
                    cafeteria_id=cafeteria_id, max_pieces=max_pieces, carbohydrate=carbohydrate, calories=calories, protein=protein, 
                    total_fat=total_fat, saturated_fat=saturated_fat, sugar=sugar, cholesterol=cholesterol,
                    fiber=fiber, sodium=sodium, potassium=potassium,iron=iron, vitamin_a=vitamin_a,
                    vitamin_c=vitamin_c, vitamin_d=vitamin_d))

                algo_state = item_choice_example(height, weight, birthdate, meals, meal_length, sex, health_goal, activity_level, meal_items)
                #print(algo_state)
                num_combination = 1

                combinations = []
                meal_length = 50
                for i in algo_state.keys():
                    num_combination *= len(algo_state[i]['items'])

                for large_id in algo_state['large']['items']:
                    for small1_id in algo_state['small1']['items']:
                        for small2_id in algo_state['small2']['items']:
                            combinations.append([large_id, small1_id, small2_id])
                
                for combination_count,combination in enumerate(combinations):          
                    state=[]
                    for ind_combination, id_combination in enumerate(combination):
                        item_index = short_list_df[short_list_df.pk == id_combination].index

                        if float(short_list_df.loc[item_index,'portion_volume']) < 0:
                            discrete=True
                        else:
                            discrete=False
                        if ind_combination == 0:
                            if discrete:
                                max_volume=int(short_list_df.loc[item_index,'max_pieces'])
                                portion_volume=float(short_list_df.loc[item_index, 'portion_volume'])*-1
                            else:
                                max_volume=610
                                portion_volume = float(short_list_df.loc[item_index, 'portion_volume'])
                        else:
                            if discrete:
                                max_volume = int(short_list_df.loc[item_index, 'max_pieces'])
                                portion_volume=float(short_list_df.loc[item_index, 'portion_volume'])*-1
                            else:
                                max_volume=270
                                portion_volume=float(short_list_df.loc[item_index, 'portion_volume'])

                        carbohydrate = float(short_list_df.loc[item_index,'carbohydrate'])
                        calories = float(short_list_df.loc[item_index,'calories'])
                        protein = float(short_list_df.loc[item_index,'protein'])
                        total_fat = float(short_list_df.loc[item_index,'total_fat'])
                        saturated_fat = float(short_list_df.loc[item_index,'saturated_fat'])
                        sugar= float(short_list_df.loc[item_index,'sugar'])
                        cholesterol=float(short_list_df.loc[item_index,'cholesterol'])
                        fiber= float(short_list_df.loc[item_index,'fiber'])
                        sodium=float(short_list_df.loc[item_index,'sodium'])
                        potassium=float(short_list_df.loc[item_index,'potassium'])
                        calcium=float(short_list_df.loc[item_index,'calcium'])
                        iron=float(short_list_df.loc[item_index,'iron'])
                        vitamin_a=float(short_list_df.loc[item_index,'vitamin_a'])
                        vitamin_c=float(short_list_df.loc[item_index,'vitamin_c'])
                        vitamin_d=float(short_list_df.loc[item_index,'vitamin_d'])                    
                        
                        nutrition = Nutrition(calories=calories,carbohydrate=carbohydrate,protein=protein,
                        total_fat=total_fat,saturated_fat=saturated_fat,trans_fat=0,sugar=sugar,cholesterol=cholesterol,
                        fiber=fiber,sodium=sodium,potassium=potassium,calcium=calcium,iron=iron,vitamin_a=vitamin_a,
                        vitamin_c=vitamin_c,vitamin_d=vitamin_d)

                        state.append(PlateSectionState(discrete=discrete, id=id_combination, max_volume=max_volume, 
                        portion_volume=portion_volume, nutrition=nutrition))
                    
                    algo_portion_state = item_portion_example(height, weight, birthdate, meals, meal_length, sex, health_goal, activity_level, state)
                    #print('Result Combination:', combination_count+1)

                    #print(algo_portion_state)
                    d = [ind_student+52, sex, height, weight, health_goal, activity_level, age, day, meal_name, num_combination, combination_count+1, combination]
                    d += retrieve_result(algo_portion_state)

                    DATA.append(d)
            else:
                pass
        if ind_student % 10 == 0:
            DATA_df_inter =  pd.DataFrame(DATA, columns=['Student_Number', 'Sex', 'Height', 'Weight', 'Health_Goal', 'Activity', 'Age', 
            'Date', 'Meal_Name','Total_Combination', 'Current_Combination', 'Combination', 
            'Vol_Large', 'Vol_Small1', 'Vol_Small2']+NUTRIENTS)
            DATA_df_inter.to_csv('test_inter.csv', index=False)    

    DATA_df = pd.DataFrame(DATA, columns=['Student_Number', 'Sex', 'Height', 'Weight', 'Health_Goal', 'Activity', 'Age', 
    'Date', 'Meal_Name','Total_Combination', 'Current_Combination', 'Combination', 
    'Vol_Large', 'Vol_Small1', 'Vol_Small2']+NUTRIENTS)
    DATA_df.to_csv('test.csv', index=False)


   
 
