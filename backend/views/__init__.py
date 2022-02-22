from django.shortcuts import render
from django.urls import path, include, reverse

from backend.models import MealItem, StudentProfile
from backend.views.data_admin import data_admin_view


@data_admin_view
def debug_view(request):
    # algorithm_test
    u = StudentProfile.objects.get(pk=10)
    l = MealItem.objects.get(name='CHE 21 Brown Rice and Lentils with Arugula')
    s1 = MealItem.objects.get(name='CHE 18 Mongolian Beef')
    s2 = MealItem.objects.get(name='CHE 17 Roasted Vegetable Medley')

    return render(request, 'debug/root.html', {
        'algorithm_test_url': reverse('da_test_algorithm', args=[u.pk, l.pk, s1.pk, s2.pk]),
    })


urlpatterns = [
    path('', debug_view, name='root_debug_view'),

    # path('login/', view_login, name='login'), # TODO: School admin login/logout, iteration 2
    # path('logout/', view_logout, name='logout'),

    path('data_admin/', include('backend.views.data_admin')),
    path('api/', include('backend.views.api')),
    path('jobs/', include('backend.views.jobs')),
]
