from rest_framework import serializers

from backend.models import Ingredient, MealItem, MealSelection, NutritionalInfo
from data.babson.parse_excel import get_meal_items

SCHOOL_ID = 10


def clean_old():
    MealSelection.objects.filter(school__id=SCHOOL_ID).delete()
    NutritionalInfo.objects.filter(mealitem__school__id=SCHOOL_ID).delete()
    MealItem.objects.filter(school__id=SCHOOL_ID).delete()
    Ingredient.objects.filter(school__id=SCHOOL_ID).delete()


def add_meal_items():
    class NutritionalInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = NutritionalInfo
            fields = '__all__'

    class MealItemSerializer(serializers.ModelSerializer):
        class Meta:
            model = MealItem
            exclude = ['nutrition', 'ingredients']

    meal_items, _ = get_meal_items()

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
    MealItem.objects.bulk_create(objs)


def setup():
    clean_old()
    add_meal_items()
