import datetime

from backend.algorithm.common import ATHLETIC_PERFORMANCE, MALE, MODERATE, Nutrition, VEGETABLE
from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing, PlateSectionState, MealItemSpec
from backend.algorithm.requirements import StudentProfileSpec, nutritional_info_for


def item_choice_example():
    profile = StudentProfileSpec(
        height=1.78,
        weight=80,
        birthdate=datetime.date(year=2003, month=11, day=30),
        meals=['breakfast', 'lunch'],
        meal_length=50,
        sex='male',
        health_goal='athletic_performance',
        activity_level='moderate'
    )

    algo = MealItemSelector(
        profile=profile,
        items=[
            MealItemSpec(
                id=1018,
                category='vegetable',
                cafeteria_id='123456.789',
                portion_volume=101,
                max_pieces=-1,
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
            ),
            MealItemSpec(
                id=1019,
                category='protein',
                cafeteria_id='123456.789',
                portion_volume=-2,
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
            # ...list of MealItemSpec objects...
        ],
        large_portion_max=610,
        small_portion_max=270,
        sa_alpha=0.99,
        sa_lo=0.01,
        seed=69696969
    )
    algo.run_algorithm()
    algo.result_obj()  # Check this for result


def item_portion_example():
    profile = StudentProfileSpec(
        height=1.78,
        weight=80,
        birthdate=datetime.date(year=2003, month=11, day=30),
        meals=['breakfast', 'lunch'],
        meal_length=50,
        sex='male',
        health_goal='athletic_performance',
        activity_level='moderate'
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


if __name__ == '__main__':
    item_choice_example()
