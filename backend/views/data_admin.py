import functools
import itertools
import os
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import path
from django.views.generic import FormView

from backend.algorithm.item_choice import PlateSection, MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing
from backend.models import School, StudentProfile, MealSelection, MealItem, Ingredient, SchoolProfile

DATA_FIXTURE_PATH = settings.BASE_DIR / 'backend_data_parsing'
SCHOOLS = ('babson',)


def data_admin_view(fun):
    @functools.wraps(fun)
    @login_required(login_url='/admin/login/')
    def wrapper(request, *args, **kwargs):
        # if not settings.DEBUG:
        #     return HttpResponse('Debug mode not enabled.  This is a debug-only page')

        if not request.user.is_superuser:
            return HttpResponse(
                'Only superusers may use this.<br><a href="/admin/login/?next=/">Choose another account</a>')

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if Path(DATA_FIXTURE_PATH).exists():
            files: list[Path] = list(itertools.chain(*(
                (DATA_FIXTURE_PATH / school / file
                 for file in os.listdir(DATA_FIXTURE_PATH / school) if file.endswith('.json'))
                for school in SCHOOLS)))
            self.not_found = False
        else:
            files: list[Path] = []
            self.not_found = True

        self.fields['fixtures'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple,
            choices=[(str(file), str(file.relative_to(file.parent.parent))) for file in files],
        )

    def clean(self):
        cleaned_data = super().clean()
        if self.not_found:
            self.add_error('fixtures', f'Directory {DATA_FIXTURE_PATH} was not found.  No fixtures can be loaded.  '
                                       f'Maybe you are working on prod? (the submodule is not copied over)')
        return cleaned_data


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


def resolve_form_id(model, cleaned_data, field):
    if field_id := cleaned_data.get(field):
        try:
            cleaned_data[field] = model.objects.get(pk=field_id)
        except model.DoesNotExist as e:
            raise ValidationError(str(e))


class AlgorithmTestChoicesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['profile'] = forms.ChoiceField(
            label='Profile (only pk <= 20)',
            choices=tuple(
                (profile.user.id, str(profile)) for profile in
                StudentProfile.objects.filter(user_id__lte=20).order_by('user_id')
            ),
            required=True
        )
        self.fields['meal'] = forms.ChoiceField(
            label='Meal',
            choices=tuple(
                (meal.id, f'{meal.name} - {meal.school}') for meal in MealSelection.objects.all().order_by('id')
            ),
            required=True
        )

    def clean(self):
        cleaned_data = super().clean()
        resolve_form_id(StudentProfile, cleaned_data, 'profile')
        resolve_form_id(MealSelection, cleaned_data, 'meal')

        return cleaned_data


class AlgorithmTestPortionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        result = kwargs.pop('result', None)
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        self.fields['profile'] = forms.IntegerField(
            label='Profile (ID)',
            initial=profile.id if profile else None,
            disabled=True,
            required=True
        )
        for section in PlateSection.all():
            self.fields[section] = forms.ChoiceField(
                choices=tuple(
                    (item.id, item.name) for item in result[section]['items']
                ) if result else tuple(),
                required=True
            )

    def clean(self):
        cleaned_data = super().clean()
        resolve_form_id(StudentProfile, cleaned_data, 'profile')
        for section in PlateSection.all():
            resolve_form_id(MealItem, cleaned_data, section)

        return cleaned_data


@data_admin_view
def test_algorithm_choices(request):
    if request.method == 'POST':
        form = AlgorithmTestChoicesForm(request.POST)
        if form.is_valid():
            # TODO: add in other form, processing
            profile: StudentProfile = form.cleaned_data['profile']
            meal: MealSelection = form.cleaned_data['meal']
            alg = MealItemSelector(meal, profile)
            alg.run_algorithm()

            portions_form = AlgorithmTestPortionsForm(result=alg.result_dict, profile=profile)

            return render(request, 'data_admin/test_algorithm_choices.html', {
                'choices_form': form,
                'portions_form': portions_form
            })
    else:
        return render(request, 'data_admin/test_algorithm_choices.html', {
            'choices_form': AlgorithmTestChoicesForm(),
        })


@data_admin_view
def test_algorithm_portions(request):
    form = AlgorithmTestPortionsForm(request.POST)
    if form.is_valid():
        profile = form.cleaned_data['profile']
        large = form.cleaned_data['large']
        small1 = form.cleaned_data['small1']
        small2 = form.cleaned_data['small2']

        sa = SimulatedAnnealing(profile, large, small1, small2)
        sa.run_algorithm()
        got_info = sa.nutrition_of(sa.state)
        lo_info = sa.nutrition_of(sa.lo_state())
        hi_info = sa.nutrition_of(sa.hi_state())

        return render(request, 'data_admin/test_algorithm_portions.html', {
            'profile': profile,
            'large': large,
            'small1': small1,
            'small2': small2,
            'info': [(k, v1, v2, v3, v4) for (k, v1), (_, v2), (__, v3), (___, v4) in
                     zip(sa.req.as_dict().items(), got_info.as_dict().items(), lo_info.as_dict().items(),
                         hi_info.as_dict().items())
                     if k != '_state' and k != 'id' and k != 'name'],
            'cost': sa.final_cost,
            'runtime': sa.runtime,
            'large_size': sa.large_volume,
            'small1_size': sa.small1_volume,
            'small2_size': sa.small2_volume,
        })
    else:
        return render(request, 'data_admin/test_algorithm_portions.html', {
            'error': form.errors
        })
    # TODO: rewrite_this


@data_admin_view
def clear_cache(_):
    cache.clear()
    return HttpResponse('Cleared cache')


@data_admin_view
def debug_view(request):
    messages = []

    return render(request, 'debug/root.html', {
        'messages': messages,
    })


app_name = 'backend'

urlpatterns = [
    path('view_all/', view_all, name='view_all'),
    path('update_school_data/', data_admin_view(UpdateSchoolDataFormView.as_view()), name='update_school_data'),
    path('test_algorithm_portions/', test_algorithm_portions, name='test_algorithm_portions'),
    path('test_algorithm_choices/', test_algorithm_choices, name='test_algorithm_choices'),
    path('clear_cache/', clear_cache, name='clear_cache'),
]
