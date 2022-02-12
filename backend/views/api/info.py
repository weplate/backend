import datetime

from backend.models import School, StudentProfile, Ingredient, MealSelection
from backend.views.common import json_response, auth_endpoint

MAX_MEALS = 10


def schools(_):
    return json_response({
        'data': [{'name': school.name, 'pk': school.pk} for school in School.objects.all()]
    })


@auth_endpoint(StudentProfile)
def ingredients(request):
    profile = StudentProfile.objects.get(user=request.user)

    return json_response({
        'data': [
            {
                'name': ingredient.name,
                'pk': ingredient.pk
            } for ingredient in Ingredient.objects.filter(school=profile.school)
        ]
    })


@auth_endpoint(StudentProfile)
def meals(request):
    profile = StudentProfile.objects.get(user=request.user)
    meals = MealSelection.objects.filter(school=profile.school, timestamp__gt=datetime.datetime.now())\
        .order_by('timestamp')[:MAX_MEALS]




@auth_endpoint(StudentProfile)
def items(request, meal_id):
    pass
