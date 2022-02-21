import functools
import json
from json import JSONDecodeError

from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import path
from django.views.generic import FormView
from rest_framework import serializers

from backend.algorithm import simulated_annealing, nutritional_info_for, fast_combine
from backend.models import School, StudentProfile, MealSelection, MealItem, Ingredient, SchoolProfile, NutritionalInfo


def data_admin_view(fun):
    @functools.wraps(fun)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            return HttpResponse('Debug mode not enabled.  This is a debug-only page')

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


class UploadMealItemsForm(forms.Form):
    # school = forms.ChoiceField(choices=(), required=True)
    file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['school'].choices = tuple(((s.pk, s.name) for s in School.objects.all()))

    def clean(self):
        cleaned_data = super().clean()

        try:
            json_file_data = json.load(cleaned_data['file'])
            cleaned_data['file'] = json_file_data
        except JSONDecodeError as e:
            self.add_error('file', f'File is invalid json.  Error: {e}')

        return cleaned_data


class NutritionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalInfo
        fields = '__all__'


class MealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealItem
        exclude = ['nutrition', 'ingredients']


class UploadMealItemsFormView(FormView):
    template_name = 'data_admin/upload_meal_items.html'
    form_class = UploadMealItemsForm
    success_url = '/'

    def form_valid(self, form):
        file_data = form.cleaned_data['file']

        objs = []
        for d in file_data.values():
            ser = NutritionalInfoSerializer(data=d)
            ser.is_valid(raise_exception=True)
            objs.append(NutritionalInfo(**ser.validated_data))
        n_info_list = NutritionalInfo.objects.bulk_create(objs)
        objs.clear()
        for m_info, n_info in zip(file_data.values(), n_info_list):
            ser = MealItemSerializer(data=m_info)
            ser.is_valid(raise_exception=True)
            objs.append(MealItem(**ser.validated_data, nutrition=n_info))
        MealItem.objects.bulk_create(objs)

        return super().form_valid(form)


def test_algorithm(request, profile, large, small1, small2):
    profile = get_object_or_404(StudentProfile, pk=profile)
    large = get_object_or_404(MealItem, pk=large)
    small1 = get_object_or_404(MealItem, pk=small1)
    small2 = get_object_or_404(MealItem, pk=small2)

    want_info = nutritional_info_for(profile)
    (lc, s1c, s2c), cost, perf = simulated_annealing(large, small1, small2, want_info)
    got_info = fast_combine(large, small1, small2, lc, s1c, s2c)

    return render(request, 'data_admin/test_algorithm.html', {
        'profile': profile,
        'large': large,
        'small1': small1,
        'small2': small2,
        'info': [(k, v1, v2) for (k, v1), (_, v2) in zip(want_info.__dict__.items(), got_info.__dict__.items())
                 if k != '_state' and k != 'id' and k != 'name'],
        'cost': cost,
        'runtime': perf,
    })


urlpatterns = [
    path('view_all/', view_all, name='da_view_all'),
    path('upload_meal_items/', UploadMealItemsFormView.as_view(), name='da_upload_meal_items'),
    path('test_algorithm/<int:profile>/<int:large>/<int:small1>/<int:small2>/', test_algorithm, name='da_test_algorithm'),
]
