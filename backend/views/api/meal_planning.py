from backend.algorithm import nutritional_info_for
from backend.models import StudentProfile
from backend.views.api.api_common import dict_nutrition
from backend.views.common import auth_endpoint, json_response


@auth_endpoint(StudentProfile)
def nutritional_requirements(request):
    profile = StudentProfile.objects.get(user=request.user)

    return json_response(dict_nutrition(nutritional_info_for(profile)))