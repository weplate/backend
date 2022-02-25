import datetime
import itertools
import pathlib
import re
from collections import defaultdict

import pytz
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework import serializers

from backend.models import Ingredient, MealItem, MealSelection, NutritionalInfo, School
from data.babson.parse_items_excel import get_meal_items

SCHOOL_ID = 10
VERSION = 0
FILE_DIR = pathlib.Path(__file__).resolve().parent

MEAL_TIMES = (
    ('breakfast', datetime.time(hour=7, minute=30)),
    ('lunch', datetime.time(hour=11)),
    ('afterlunch', datetime.time(hour=14, minute=30)),
    ('dinner', datetime.time(hour=16, minute=30)),
)
MEAL_TIMES_DICT = dict(MEAL_TIMES)

MEAL_KEYS = tuple(map(lambda x: x[0], MEAL_TIMES))
MEAL_SELECTION_COLS = [0, 1, 4, 5, 6, 7, 10]


def clean_old():
    MealSelection.objects.filter(school__id=SCHOOL_ID, version=0).delete()
    NutritionalInfo.objects.filter(mealitem__school__id=SCHOOL_ID, version=0).delete()
    MealItem.objects.filter(school__id=SCHOOL_ID, version=0).delete()
    Ingredient.objects.filter(school__id=SCHOOL_ID, version=0).delete()


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


# input is a list of tuples (meal_item, meal) (meal = 'breakfast', 'lunch', 'dinner'
def add_meals(meal_items: list[tuple[MealItem, str]]):
    # setup item dicts from meal items input
    items_by_meal = defaultdict(list)
    for item, meal in meal_items:
        items_by_meal[meal].append(item)
    items_by_meal['afterlunch'] = \
        list(filter(lambda x: x.station in ['FLAME', '500 Degrees', 'Carved and Crafted'], items_by_meal['lunch']))
    # Need to setup afterlunch meal
    items_by_name: dict[str, list[tuple[MealItem, str]]] = defaultdict(list)
    for meal, items in items_by_meal.items():
        for item in items:
            items_by_name[item.name].append((item, meal))

    # parse meals sheet
    meal_sheet: Worksheet = load_workbook(FILE_DIR / 'weekly_menus_2.xlsx', read_only=True)['Report']

    item_names_by_day: dict[datetime.date, list[str]] = defaultdict(list)
    meals: list[MealSelection] = []
    corr_items = []
    babson = School.objects.get(pk=SCHOOL_ID)

    for col in MEAL_SELECTION_COLS:
        meal_day = None
        for row in meal_sheet.iter_rows(13, 1587):
            val = row[col].value
            if val is None:
                continue
            elif m := re.match(r'\w+ \((\d+)/(\d+)/(\d+)\)', val):
                meal_day = datetime.date(year=int(m.group(3)), month=int(m.group(1)), day=int(m.group(2)))
            else:
                item_names_by_day[meal_day].append(val)
    print('Parsed spreadsheet')

    # Create objects
    print(items_by_name)
    for day, item_names in item_names_by_day.items():
        print(day, len(item_names))
        for name in item_names:
            if len(items_by_name[name]):
                print(name, len(items_by_name[name]))

        _i = itertools.chain(*(items_by_name[name] for name in item_names))
        _snd = lambda t: t[1]

        for meal, items in itertools.groupby(sorted(_i, key=_snd), key=_snd):
            dt = datetime.datetime.combine(day, MEAL_TIMES_DICT[meal],
                                           pytz.timezone('America/Toronto'))  # The Waterloo student did this one
            meals.append(MealSelection(name=f'{meal.title()} on {day.strftime("%A, %B")} {day.day}, {day.year}',
                                       group=meal,
                                       timestamp=dt,
                                       school=babson,
                                       version=VERSION))
            corr_items.append(items)
    print('Created Meal Selection Objects')

    meals = MealSelection.objects.bulk_create(meals)
    print(f'Created {len(meals)} meal objects')
    for idx, (m, i) in enumerate(zip(meals, corr_items), start=1):
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
