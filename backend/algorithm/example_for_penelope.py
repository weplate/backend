import datetime

from backend.algorithm.common import ATHLETIC_PERFORMANCE, MALE, MODERATE, Nutrition
from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing, PlateSectionState
from backend.algorithm.requirements import StudentProfileSpec, nutritional_info_for


def item_choice_example():
    profile = StudentProfileSpec(
        height=1.78,
        weight=80,
        birthdate=datetime.date(year=2003, month=11, day=30),
        meals=['breakfast', 'lunch'],
        meal_length=50,
        sex=MALE,
        health_goal=ATHLETIC_PERFORMANCE,
        activity_level=MODERATE
    )

    algo = MealItemSelector(
        profile=profile,
        items=[
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


if __name__ == '__main__':
    item_choice_example()
