from backend.models import NutritionalInfo, Ingredient, MealItem, MealSelection
from backend.views.common import without_keys


def dict_ingredient(ingredient: Ingredient):
    return {'name': ingredient.name, 'pk': ingredient.pk}


def dict_school(school):
    return {'name': school.name, 'pk': school.pk}


def dict_nutrition(nutrition: NutritionalInfo):
    return without_keys(nutrition.__dict__, ['_state']) | {'pk': nutrition.pk}


def dict_meal_item(meal_item: MealItem):
    return {
        'pk': meal_item.pk,
        'name': meal_item.name,
        'station': meal_item.station,
        'nutrition': dict_nutrition(meal_item.nutrition or NutritionalInfo()),
        'ingredients': list(map(dict_ingredient, meal_item.ingredients.all())),
        'school': dict_school(meal_item.school)
    }


def dict_meal_selection(meal: MealSelection):
    return {
        'pk': meal.pk,
        'name': meal.name,
        'group': meal.group,
        'timestamp': meal.timestamp.isoformat(),
        'items': list(map(dict_meal_item, meal.items.all())),
        'school': dict_school(meal.school)
    }
