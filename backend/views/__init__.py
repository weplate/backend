from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from ..models import School, StudentProfile, MealSelection, MealItem, Ingredient, SchoolProfile


def debug_view(request):
    if not settings.DEBUG:
        return HttpResponse('Debug mode not enabled.  This is a debug-only page')

    return render(request, 'debug/root.html', {
        'schools': School.objects.all(),
        'student_profiles': StudentProfile.objects.all(),
        'meals': MealSelection.objects.all(),
        'meal_items': MealItem.objects.all(),
        'ingredients': Ingredient.objects.all(),
        'school_profiles': SchoolProfile.objects.all()
    })


urlpatterns = [
    path('', debug_view, name='root_debug_view'),

    # path('login/', view_login, name='login'), # TODO: School admin login/logout, iteration 2
    # path('logout/', view_logout, name='logout'),

    path('api/', include('backend.views.api')),

    # Jobs
    path('jobs/', include('backend.views.jobs'))
]
