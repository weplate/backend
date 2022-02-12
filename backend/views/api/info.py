import datetime

from django.shortcuts import get_object_or_404

from backend.models import School, StudentProfile, Ingredient, MealSelection
from backend.views.api.api_common import dict_ingredient, dict_school, dict_meal_selection, dict_meal_item
from backend.views.common import json_response, auth_endpoint

MAX_MEALS = 5


def schools(_):
    return json_response({
        'data': [dict_school(school) for school in School.objects.all()]
    })


@auth_endpoint(StudentProfile)
def ingredients(request):
    profile = StudentProfile.objects.get(user=request.user)

    return json_response({
        'data': [dict_ingredient(ingredient) for ingredient in Ingredient.objects.filter(school=profile.school)]
    })


@auth_endpoint(StudentProfile)
def meals(request):
    profile = StudentProfile.objects.get(user=request.user)
    meals = MealSelection.objects.filter(school=profile.school, timestamp__gt=datetime.datetime.now()) \
                .order_by('timestamp')[:MAX_MEALS]

    return json_response({'data': [dict_meal_selection(meal) for meal in meals]})


@auth_endpoint(StudentProfile)
def items(request, meal_id):
    profile = StudentProfile.objects.get(user=request.user)
    items = get_object_or_404(MealSelection, pk=meal_id, school=profile.school).items.all()

    return json_response({'data': [dict_meal_item(item) for item in items]})
