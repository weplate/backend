from backend.models import School, StudentProfile, Ingredient
from backend.views.common import json_response, auth_endpoint


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
