import datetime
import pytz
from collections import defaultdict

from rest_framework import serializers

from backend.models import Ingredient, MealItem, MealSelection, NutritionalInfo, School
from data.babson.parse_excel import get_meal_items

SCHOOL_ID = 10


def clean_old():
    MealSelection.objects.filter(school__id=SCHOOL_ID).delete()
    NutritionalInfo.objects.filter(mealitem__school__id=SCHOOL_ID).delete()
    MealItem.objects.filter(school__id=SCHOOL_ID).delete()
    Ingredient.objects.filter(school__id=SCHOOL_ID).delete()


def add_meal_items():
    meal_items, _ = get_meal_items()

    class NutritionalInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = NutritionalInfo
            fields = '__all__'

    class MealItemSerializer(serializers.ModelSerializer):
        class Meta:
            model = MealItem
            exclude = ['nutrition', 'ingredients']

    objs = []
    for d in meal_items.values():
        ser = NutritionalInfoSerializer(data=d)
        ser.is_valid(raise_exception=True)
        objs.append(NutritionalInfo(**ser.validated_data))
    n_info_list = NutritionalInfo.objects.bulk_create(objs)
    objs.clear()
    for m_info, n_info in zip(meal_items.values(), n_info_list):
        ser = MealItemSerializer(data=m_info)
        ser.is_valid(raise_exception=True)
        objs.append(MealItem(**ser.validated_data, nutrition=n_info))

    return MealItem.objects.bulk_create(objs)


MEAL_TIMES = (
    ('Breakfast', datetime.time(hour=7, minute=30)),
    ('Lunch', datetime.time(hour=11)),
    ('Dinner', datetime.time(hour=16, minute=30)),
)

MEAL_KEYS = tuple(map(lambda x: x[0], MEAL_TIMES))

NUM_DAYS = 50


def add_meals(meal_items: list[MealItem]):
    items_by_meal = defaultdict(list)
    for item in meal_items:
        for key in MEAL_KEYS:
            if key in item.station:
                items_by_meal[key].append(item)
                break

    meals: list[MealSelection] = []
    items = []
    babson = School.objects.get(pk=SCHOOL_ID)
    for i in range(NUM_DAYS):
        for k, t in MEAL_TIMES:
            day = datetime.date.today() + datetime.timedelta(days=i)
            dt = datetime.datetime.combine(day, t,
                                           pytz.timezone('America/Toronto'))  # The Waterloo student did this one
            meals.append(MealSelection(name=f'{k} on {day.strftime("%A, %B")} {day.day}, {day.year}',
                                       group=k.lower(),
                                       timestamp=dt,
                                       school=babson))
            items.append(items_by_meal[k])

    meals = MealSelection.objects.bulk_create(meals)
    for m, i in zip(meals, items):
        m.items.set(i)
        m.save()


def setup():
    clean_old()
    meal_items = add_meal_items()
    add_meals(meal_items)
