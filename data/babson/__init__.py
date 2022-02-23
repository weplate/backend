import datetime
from collections import defaultdict

import pytz
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
    meals = []
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
        meals.append(str(m_info['meal']))

    return list(zip(MealItem.objects.bulk_create(objs), meals))


MEAL_TIMES = (
    ('breakfast', datetime.time(hour=7, minute=30)),
    ('lunch', datetime.time(hour=11)),
    ('afterlunch', datetime.time(hour=14, minute=30)),
    ('dinner', datetime.time(hour=16, minute=30)),
)

MEAL_KEYS = tuple(map(lambda x: x[0], MEAL_TIMES))

NUM_DAYS = 50


def add_meals(meal_items: list[tuple[MealItem, str]]):
    items_by_meal = defaultdict(list)
    for item, meal in meal_items:
        items_by_meal[meal].append(item)

    items_by_meal['afterlunch'] = \
        list(filter(lambda x: x.station in ['FLAME', '500 Degrees', 'Carved and Crafted'], items_by_meal['lunch']))

    meals: list[MealSelection] = []
    items = []
    babson = School.objects.get(pk=SCHOOL_ID)
    for i in range(-1, NUM_DAYS):
        for k, t in MEAL_TIMES:
            day = datetime.date.today() + datetime.timedelta(days=i)
            dt = datetime.datetime.combine(day, t,
                                           pytz.timezone('America/Toronto'))  # The Waterloo student did this one
            meals.append(MealSelection(name=f'{k.title()} on {day.strftime("%A, %B")} {day.day}, {day.year}',
                                       group=k,
                                       timestamp=dt,
                                       school=babson))
            items.append(items_by_meal[k])

    meals = MealSelection.objects.bulk_create(meals)
    print(f'Created {len(meals)} meal objects')
    for idx, (m, i) in enumerate(zip(meals, items), start=1):
        m.items.set(i)
        m.save()

        if idx % 40 == 0:
            print(f'Updated `items` field for {idx} meal objects')


def setup():
    clean_old()
    print('Cleaned old data')
    meal_items = add_meal_items()
    print(f'Added {len(meal_items)} meal items to DB')
    add_meals(meal_items)
    print('Setup complete!')
