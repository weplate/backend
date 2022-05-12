from dacite import from_dict
from django.conf import settings

from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import PlateSectionState, SimulatedAnnealing, MealItemSpec, DEFAULT_COEFFICIENTS
from backend.algorithm.requirements import nutritional_info_for, StudentProfileSpec
from backend.models import MealItem, StudentProfile, MealSelection


def plate_section_state_from_model(item: MealItem, container_volume: float, num_sections: int,
                                   section_name: str) -> PlateSectionState:
    """
    Creates a PlateSectionState (with 0 cur. volume) from a given meal item and other parameters
    @param item The meal item to create the object from
    @param container_volume The total container volume, in DB format (i.e. positive for continuous, negative integer for discrete)
    @param num_sections The number of sections this container is divided into (so the actual volume can be computed by how much of the section this occupies)
    @param section_name The name of the section (currently, "large", "small1", or "small2")
    @return A PlateSectionState object
    """
    return PlateSectionState.from_item_spec(from_dict(MealItemSpec, item.__dict__), container_volume, num_sections,
                                            section_name)


def simulated_annealing_from_model(
        profile: StudentProfile, large: list[MealItem], small1: list[MealItem], small2: list[MealItem],
        large_max_volume: float, small_max_volume: float) -> SimulatedAnnealing:
    """
    @param profile: The student to choose the portions for
    @param large: List of meal items to be put in the large section
    @param small1: List of meal items to be put in the first small section
    @param small2: List of meal items to be put in the second small section
    @param large_max_volume: Size of the large plate section, in mL
    @param small_max_volume: Size of the small plate section, in mL
    @return: Returns SimulatedAnnealing (portion selector) object using Django DB model objects instead of the
    dataclass objects normally used
    """

    initial_state = []
    for items, container_volume, section_name in zip((large, small1, small2),
                                                     (large_max_volume, small_max_volume, small_max_volume),
                                                     ('large', 'small1', 'small2')):
        for item in items:
            initial_state.append(plate_section_state_from_model(item, container_volume, len(items), section_name))

    return SimulatedAnnealing(profile=from_dict(StudentProfileSpec, profile.__dict__),
                              state=initial_state,
                              coefficients=DEFAULT_COEFFICIENTS,
                              alpha=0.999,
                              smallest_temp=0.0005,
                              seed=20210226 if settings.PROD else -1)


def result_object_for_simulated_annealing(obj: SimulatedAnnealing) -> list[dict[str, any]]:
    """
    @param obj: Object to generate result object from
    @return: Returns the result of the algorithm according to the endpoint specifications in the README.md.  The result will be in a JSON-serializable format
    """
    return [{
        'id': int(state.id),
        'volume': state.format_volume(),
        'total_volume': state.format_max_volume(),
        'section': state.section_name
    } for state in obj.state]


def meal_item_selector_from_model(meal: MealSelection, profile: StudentProfile,
                                  large_portion_max: float, small_portion_max: float):
    """
    Creates a MealItemSelector class from Django model objects rather than the expected dataclasses
    @param meal: The meal to choose items from
    @param profile: The student to choose the items for
    @param large_portion_max: The size of the large container section (in mL)
    @param small_portion_max: The size of the small container sections (in mL)
    @return: Returns MealItemSelector class created from Django model objects rather than the expected dataclasses
    """
    return MealItemSelector(profile=from_dict(StudentProfileSpec, profile.__dict__),
                            items=[from_dict(MealItemSpec, item.__dict__) for item in meal.items.all()],
                            large_portion_max=large_portion_max,
                            small_portion_max=small_portion_max,
                            coefficients=DEFAULT_COEFFICIENTS,
                            sa_alpha=0.99,
                            sa_lo=0.01,
                            seed=20210226 if settings.PROD else -1)
