import functools
import itertools
import os
from pathlib import Path

from django import forms
from django.core.cache import cache
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import path, reverse
from django.views.generic import FormView

from backend.algorithm.portion import SimulatedAnnealing
from backend.models import School, StudentProfile, MealSelection, MealItem, Ingredient, SchoolProfile

DATA_FIXTURE_PATH = settings.BASE_DIR / 'backend_data_parsing'
SCHOOLS = ('babson',)


def data_admin_view(fun):
    @functools.wraps(fun)
    def wrapper(request, *args, **kwargs):
        # if not settings.DEBUG:
        #     return HttpResponse('Debug mode not enabled.  This is a debug-only page')

        if not request.user.is_superuser:
            return HttpResponse('Only superusers may use this.')

        return fun(request, *args, **kwargs)

    return wrapper


@data_admin_view
def view_all(request):
    return render(request, 'data_admin/view_all.html', {
        'schools': School.objects.all(),
        'student_profiles': StudentProfile.objects.all(),
        'meals': MealSelection.objects.all(),
        'meal_items': MealItem.objects.all(),
        'ingredients': Ingredient.objects.all(),
        'school_profiles': SchoolProfile.objects.all()
    })


class UpdateSchoolDataForm(forms.Form):
    files: list[Path] = list(itertools.chain(*(
        (DATA_FIXTURE_PATH / school / file
         for file in os.listdir(DATA_FIXTURE_PATH / school) if file.endswith('.json'))
        for school in SCHOOLS)))

    fixtures = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[(str(file), str(file.relative_to(file.parent.parent))) for file in files],
    )


class UpdateSchoolDataFormView(FormView):
    template_name = 'data_admin/update_school_data.html'
    form_class = UpdateSchoolDataForm
    success_url = '/'

    def form_valid(self, form):
        # print(form.cleaned_data['fixtures'])
        with transaction.atomic():
            for fixture_path in form.cleaned_data['fixtures']:
                print(f'Loading fixture path {fixture_path}')
                call_command('loaddata', fixture_path)

        return super().form_valid(form)


@data_admin_view
def test_algorithm(request, profile, large, small1, small2):
    profile = get_object_or_404(StudentProfile, pk=profile)
    large = get_object_or_404(MealItem, pk=large)
    small1 = get_object_or_404(MealItem, pk=small1)
    small2 = get_object_or_404(MealItem, pk=small2)

    sa = SimulatedAnnealing(profile, large, small1, small2)
    sa.run_algorithm()
    got_info = sa.nutrition_of(sa.state)
    lo_info = sa.nutrition_of(sa.lo_state())
    hi_info = sa.nutrition_of(sa.hi_state())

    return render(request, 'data_admin/test_algorithm.html', {
        'profile': profile,
        'large': large,
        'small1': small1,
        'small2': small2,
        'info': [(k, v1, v2, v3, v4) for (k, v1), (_, v2), (__, v3), (___, v4) in
                 zip(sa.req.as_dict().items(), got_info.as_dict().items(), lo_info.as_dict().items(), hi_info.as_dict().items())
                 if k != '_state' and k != 'id' and k != 'name'],
        'cost': sa.final_cost,
        'runtime': sa.runtime,
        'large_size': sa.large_volume,
        'small1_size': sa.small1_volume,
        'small2_size': sa.small2_volume,
    })


@data_admin_view
def clear_cache(_):
    cache.clear()
    return HttpResponse('Cleared cache')


urlpatterns = [
    path('view_all/', view_all, name='da_view_all'),
    path('update_school_data/', data_admin_view(UpdateSchoolDataFormView.as_view()), name='da_update_school_data'),
    path('test_algorithm/<int:profile>/<int:large>/<int:small1>/<int:small2>/', test_algorithm, name='da_test_algorithm'),
    path('clear_cache/', clear_cache, name='da_clear_cache'),
]


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