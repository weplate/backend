import functools
import importlib

from django import forms
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import path, reverse
from django.views.generic import FormView

from backend.algorithm import simulated_annealing, nutritional_info_for, fast_combine, LARGE_PORTION_MAX, \
    SMALL_PORTION_MAX
from backend.models import School, StudentProfile, MealSelection, MealItem, Ingredient, SchoolProfile


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
    module = forms.CharField(max_length=256)

    def clean(self):
        cleaned_data = super().clean()

        try:
            cleaned_data['module'] = (module := importlib.import_module(cleaned_data['module']))
            if not hasattr(module, 'setup'):
                self.add_error('module', f'Module has no setup function')
        except ImportError as e:
            self.add_error('module', f'Error while importing module: {e}')

        return cleaned_data


class UpdateSchoolDataFormView(FormView):
    template_name = 'data_admin/update_school_data.html'
    form_class = UpdateSchoolDataForm
    success_url = '/'

    def form_valid(self, form):
        form.cleaned_data['module'].setup()
        return super().form_valid(form)


@data_admin_view
def test_algorithm(request, profile, large, small1, small2):
    profile = get_object_or_404(StudentProfile, pk=profile)
    large = get_object_or_404(MealItem, pk=large)
    small1 = get_object_or_404(MealItem, pk=small1)
    small2 = get_object_or_404(MealItem, pk=small2)

    want_info = nutritional_info_for(profile)
    (lc, s1c, s2c), cost, perf = simulated_annealing(large, small1, small2, want_info)
    got_info = fast_combine(large, small1, small2, lc, s1c, s2c)

    lo_info = fast_combine(large, small1, small2, LARGE_PORTION_MAX / 2, SMALL_PORTION_MAX / 2, SMALL_PORTION_MAX / 2)
    hi_info = fast_combine(large, small1, small2, LARGE_PORTION_MAX, SMALL_PORTION_MAX, SMALL_PORTION_MAX)

    return render(request, 'data_admin/test_algorithm.html', {
        'profile': profile,
        'large': large,
        'small1': small1,
        'small2': small2,
        'info': [(k, v1, v2, v3, v4) for (k, v1), (_, v2), (__, v3), (___, v4) in
                 zip(want_info.__dict__.items(), got_info.__dict__.items(), lo_info.__dict__.items(), hi_info.__dict__.items())
                 if k != '_state' and k != 'id' and k != 'name'],
        'cost': cost,
        'runtime': perf,
        'large_size': lc,
        'small1_size': s1c,
        'small2_size': s2c,
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