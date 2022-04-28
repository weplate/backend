import functools
import itertools

from django import forms
from django.test.client import Client
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import path

from backend.algorithm.item_choice import PlateSection, MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing
from backend.models import School, StudentProfile, MealSelection, MealItem, Ingredient, ImageQueueEntry
from backend.views.jobs import get_job_results


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
    })


def resolve_form_id(model, cleaned_data, field):
    if field_id := cleaned_data.get(field):
        try:
            cleaned_data[field] = model.objects.get(pk=field_id)
        except model.DoesNotExist as e:
            raise ValidationError(str(e))


PLATE_SIZES = (
    (610, 270),
    (800, 400)
)
PLATE_SIZE_TUPLE = tuple(
    (f'{size[0]},{size[1]}', f'Large: {size[0]}mL, Small: {size[1]}mL') for size in PLATE_SIZES
)


def update_plate_sizes(cleaned_data):
    if plate_sizes := cleaned_data.get('plate_sizes', None):
        cleaned_data['plate_sizes'] = tuple(map(int, plate_sizes.split(',', maxsplit=1)))
    return cleaned_data


class AlgorithmTestChoicesForm(forms.Form):
    plate_sizes = forms.ChoiceField(
        label='Plate Sizes',
        choices=PLATE_SIZE_TUPLE
    )

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

        return update_plate_sizes(cleaned_data)


class AlgorithmTestPortionsForm(forms.Form):
    plate_sizes = forms.ChoiceField(
        label='Plate Sizes',
        choices=PLATE_SIZE_TUPLE,
        required=True,
    )
    profile = forms.IntegerField(
        label='Profile (ID)',
        required=True,
    )

    def __init__(self, *args, **kwargs):
        result = kwargs.pop('result', None)
        super().__init__(*args, **kwargs)

        if result:
            for section in PlateSection.all():
                self.fields[section] = forms.ChoiceField(
                    choices=tuple(
                        (lambda item: (item.id, item.name))(MealItem.objects.get(id=id)) for id in
                        result[section]['items']
                    ) if result else tuple(),
                    required=True
                )
        else:
            for section in PlateSection.all():
                self.fields[section] = forms.CharField(max_length=32, required=True)

    def clean(self):
        cleaned_data = super().clean()
        resolve_form_id(StudentProfile, cleaned_data, 'profile')
        for section in PlateSection.all():
            resolve_form_id(MealItem, cleaned_data, section)

        return update_plate_sizes(cleaned_data)


@data_admin_view
def test_algorithm_choices(request):
    if request.method == 'POST':
        form = AlgorithmTestChoicesForm(request.POST)
        if form.is_valid():
            # TODO: add in other form, processing
            profile: StudentProfile = form.cleaned_data['profile']
            meal: MealSelection = form.cleaned_data['meal']
            plate_sizes: tuple[float, float] = form.cleaned_data['plate_sizes']
            alg = MealItemSelector(meal, profile, plate_sizes[0], plate_sizes[1])
            alg.run_algorithm()

            portions_form = AlgorithmTestPortionsForm({
                'plate_sizes': f'{plate_sizes[0]},{plate_sizes[1]}',
                'profile': profile.id
            }, result=alg._result_obj)

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
        plate_sizes = form.cleaned_data['plate_sizes']

        sa = SimulatedAnnealing(profile, large, small1, small2, *plate_sizes)
        sa.run_algorithm()
        got_info = sa.nutrition_of(sa.state)
        lo_info = sa.nutrition_of(sa.lo_state())
        hi_info = sa.nutrition_of(sa.hi_state())

        return render(request, 'data_admin/test_algorithm_portions.html', {
            'form': form,

            'profile': profile,
            'large': large,
            'small1': small1,
            'small2': small2,
            'info': [(k, v1, v2, v3, v4, v5) for (k, v1), (_, v2), (__, v3), (___, v4), (____, v5) in
                     zip(sa.lo_req.as_dict().items(), sa.hi_req.as_dict().items(), got_info.as_dict().items(),
                         lo_info.as_dict().items(),
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
            'form': form,
            'error': form.errors
        })
    # TODO: rewrite_this


@data_admin_view
def debug_view(request):
    messages = []

    return render(request, 'data_admin/root.html', {
        'messages': messages,
    })


class AddSchoolAccountForm(forms.Form):
    username = forms.EmailField(max_length=64, required=True)
    password = forms.CharField(max_length=64, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'] = forms.ChoiceField(
            choices=tuple(
                (school.id, f'{school.name} (ID: {school.id})') for school in School.objects.all()
            ),
            required=True
        )

    def clean(self):
        cleaned_data = super().clean()
        resolve_form_id(School, cleaned_data, 'school')
        return cleaned_data


def retrieve_permissions(codenames):
    """
    Given a list of codenames, it retrieves the list of permissions associated with those codenames.  Validity is not
    checked
    """
    return tuple(Permission.objects.get(codename=codename) for codename in codenames)


def school_permission(school: School):
    """
    Given a school object, retrieves (or creates) a permission associating the user with that school
    """
    perm, created = Permission.objects.get_or_create(
        codename=f'admin_school.{school.id}',
        defaults=dict(
            name=f'Administrator of {school}',
            content_type=ContentType.objects.get_for_model(School)
        )
    )
    if created:
        perm.save()

    return perm


@data_admin_view
def add_school_account(request):
    messages = []
    form = AddSchoolAccountForm()
    if request.method == 'POST':
        form = AddSchoolAccountForm(request.POST)
        if form.is_valid():
            data = dict(**form.cleaned_data)
            school: School = data.pop('school')

            try:
                user = User.objects.create_user(**data,
                                                email=data['username'],
                                                is_staff=True,
                                                first_name=f'{school.name}: {data["username"]}')
                user.save()

                perms = retrieve_permissions(
                    tuple(f'{t}_{m}' for t, m in itertools.product(('add', 'change', 'delete', 'view'),
                                                                   ('mealitem', 'mealselection', 'ingredient')))) \
                        + (school_permission(school),)
                user.user_permissions.add(*perms)
                user.save()

                messages.append(f'Successfully created school user {user.email} for {school.name}')
            except Exception as e:
                messages.append(f'Error: {e}')

    return render(request, 'data_admin/add_school_account.html', {
        'form': form,
        'messages': messages,
        'staff': User.objects.filter(is_staff=True, is_superuser=False)
    })


class SelectJobForm(forms.Form):
    job = forms.ChoiceField(choices=(
        (f'/jobs/{job}/', job) for job in ('clear_tokens', 'clear_cache', 'send_push')
    ))


@data_admin_view
def jobs(request):
    message = None
    if request.method == 'POST':
        form = SelectJobForm(data=request.POST)
        if form.is_valid():
            endpoint = form.cleaned_data['job']
            c = Client()
            response = c.get(endpoint, **{'X-Appengine-Cron': 'True'})
            message = f'Job {endpoint} got\n' \
                      f'- {response}'
    else:
        form = SelectJobForm()

    return render(request, 'data_admin/jobs.html', {
        'jobs': get_job_results(),
        'form': form,
        'message': message
    })


class ImageQueueDecisionForm(forms.Form):
    queue_entry = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    # https://stackoverflow.com/questions/8542839/django-form-with-booleanfield-always-invalid-unless-checked
    accept = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()

        queue_entry_id = cleaned_data['queue_entry']
        if queue_entry := ImageQueueEntry.objects.filter(id=queue_entry_id).first():
            cleaned_data['queue_entry'] = queue_entry
        else:
            self.add_error('queue_entry', 'Queue entry ID does not correspond to actual queue entry')

        return cleaned_data


@data_admin_view
def verify_item_image(request):
    errors = None
    if request.method == 'POST':
        form = ImageQueueDecisionForm(request.POST)
        if form.is_valid():
            obj: ImageQueueEntry = form.cleaned_data['queue_entry']
            if form.cleaned_data['accept']:
                if obj.item.image:  # delete old image
                    obj.item.image.delete(save=False)
                obj.item.image = obj.image
                obj.item.save()
            else:
                obj.image.delete(save=False)  # Delete image
            obj.delete()
        else:
            print(form.errors)
            errors = form.errors

    first = ImageQueueEntry.objects.order_by('timestamp').first()
    return render(request, 'data_admin/verify_item_image.html', {
        'queue_entry': first,
        'num_queue_entries': ImageQueueEntry.objects.count(),
        'errors': errors
    } | ({
             'form_accept': ImageQueueDecisionForm(initial={'queue_entry': str(first.id), 'accept': True}),
             'form_reject': ImageQueueDecisionForm(initial={'queue_entry': str(first.id), 'accept': False}),
         } if first else {}))


app_name = 'backend'

urlpatterns = [
    path('view_all/', view_all, name='view_all'),
    path('test_algorithm_portions/', test_algorithm_portions, name='test_algorithm_portions'),
    path('test_algorithm_choices/', test_algorithm_choices, name='test_algorithm_choices'),
    path('jobs', jobs, name='jobs'),
    path('add_school_account/', add_school_account, name='add_school_account'),
    path('verify_item_image/', verify_item_image, name='verify_item_image')
]
