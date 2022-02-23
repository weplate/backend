from django.shortcuts import render
from django.urls import path, include, reverse

from backend.models import MealItem, StudentProfile
from backend.views.data_admin import data_admin_view


@data_admin_view
def debug_view(request):
    messages = []

    # algorithm_test
    try:
        u = StudentProfile.objects.get(pk=10)
        l = MealItem.objects.get(name__iexact='Cilantro Rice')
        s1 = MealItem.objects.get(name__iexact='Chicken Ratatouille')
        s2 = MealItem.objects.get(name__iexact='Chopped Kale Salad with Beets')
        algo_test_url = reverse('da_test_algorithm', args=[u.pk, l.pk, s1.pk, s2.pk])
    except MealItem.DoesNotExist as e:
        algo_test_url = reverse('da_test_algorithm', args=[1, 1, 1, 1])
        messages.append(f'Could not retrieve object for algorithm test: {e}')

    return render(request, 'debug/root.html', {
        'algorithm_test_url': algo_test_url,
        'messages': messages,
    })


urlpatterns = [
    path('', debug_view, name='root_debug_view'),

    # path('login/', view_login, name='login'), # TODO: School admin login/logout, iteration 2
    # path('logout/', view_logout, name='logout'),

    path('data_admin/', include('backend.views.data_admin')),
    path('api/', include('backend.views.api')),
    path('jobs/', include('backend.views.jobs')),
]
