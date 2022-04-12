import sys
from pathlib import Path
sys.path[0] = str(Path(sys.path[0]).parent.parent)
print(sys.path[0])
import datetime
import pandas as pd
import os
from backend.algorithm.common import ATHLETIC_PERFORMANCE, MALE, MODERATE, Nutrition, VEGETABLE
from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing, PlateSectionState, MealItemSpec
from backend.algorithm.requirements import StudentProfileSpec, nutritional_info_for


NUTRITION_TABLE_LATEST = os.path.join(sys.path[0], 'backend_data_parsing/babson/master_nutrition/nutrition_table.csv')
MENU_LATEST= os.path.join(sys.path[0], 'backend_data_parsing/babson/master_menu/menu.csv')

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


def item_portion_example(height):#, weight, birthdate, meals, meal_lenth, sex, health_goal, activity_level):
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


def item_portion_example(height):#, weight, birthdate, meals, meal_lenth, sex, health_goal, activity_level):
    profile = StudentProfileSpec(
        height=height,
        weight=80,
        birthdate=datetime.date(year=2003, month=11, day=30),
        meals=['breakfast', 'lunch'],
        meal_length=50,
        sex=MALE,
        health_goal=ATHLETIC_PERFORMANCE,
        activity_level=MODERATE
    )
    lo_req, hi_req = nutritional_info_for(profile)
    algo = SimulatedAnnealing(
        lo_req=lo_req,
        hi_req=hi_req,
        state=[
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
            )  # more obviously...
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

if __name__ == '__main__':
    master_nutrition_df = pd.read_csv(NUTRITION_TABLE_LATEST, 
    converters={'cafeteria_id': lambda x: str(x), 'category': lambda x: str(x)})
    master_menu_df = pd.read_csv(MENU_LATEST, 
    converters={'cafeteria_id': lambda x: str(x), 'category': lambda x: str(x)})
    height = 1.78
    weight = 80
    birthdate = datetime.date(year=2003, month=11, day=30)
    meals = ['breakfast', 'lunch']
    meal_length = 50
    sex = MALE
    health_goal = ATHLETIC_PERFORMANCE
    activity_level = MODERATE

    #for ind, menu_row in master_menu_df.iterrows():
        #menu = eval(menu_row['items']) #pk
    menu = [1047, 1021, 1014, 1036, 1037, 1056, 1040]
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
        print(algo_state)
    else:
        pass