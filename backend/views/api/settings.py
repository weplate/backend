# List of properties to write
from backend.models import StudentProfile, School, MealItem, Ingredient
from backend.views.common import auth_endpoint, err_response, ok_response, json_response


def type_check(t):
    return lambda o: type(o) == t


def pk_check(table):
    return lambda o: table.objects.filter(id=o).exists()


def pk_list_check(table):
    return lambda o: type(o) == list and all(map(pk_check(table), o))


def model_choices_check(l):
    def func(o):
        for prop, prop_name in l:
            if prop == o:
                return True
        return False

    return func


STUDENT_PROPS = {
    'school': pk_check(School),
    'name': type_check(str),
    'height': type_check(float),
    'age': type_check(int),
    'weight': type_check(float),
    'sex': model_choices_check(StudentProfile.SEXES),
    'health_goal': model_choices_check(StudentProfile.HEALTH_GOALS),
    'ban': pk_list_check(MealItem),
    'favour': pk_list_check(MealItem),
    'allergies': pk_list_check(Ingredient)
}


@auth_endpoint(table=StudentProfile)
def update(request):
    profile = StudentProfile.objects.get(user=request.user)
    upd = []

    for prop_key, prop_verify in STUDENT_PROPS:
        if prop_key in request.POST:
            prop_val = request.POST[prop_key]
            if prop_verify(prop_val):
                setattr(profile, prop_key, prop_val)
                upd.append(prop_key)
            else:
                return err_response(f'Could not update setting, ')

    return ok_response(f'Updated settings {" ".join(upd)}')


@auth_endpoint(table=StudentProfile)
def fetch(request):
    resp = {}
    profile = StudentProfile.objects.get(user=request.user)

    for prop_key, _ in STUDENT_PROPS:
        resp[prop_key] = getattr(profile, prop_key)

    # Other fields, in notion
    resp['school_name'] = profile.school.name
    resp['ban_names'] = [obj.name for obj in profile.ban]
    resp['favour_names'] = [obj.name for obj in profile.favour]
    resp['allergies_names'] = [obj.name for obj in profile.allergies]

    return json_response(resp)
