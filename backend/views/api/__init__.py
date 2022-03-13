from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .info import SchoolViewSet, IngredientViewSet, MealSelectionViewSet, SchoolMealItemsViewSet
from .meal_planning import NutritionalRequirementsViewSet, SuggestViewSet
from .auth import register_student_view, check_email_view, verify_email_post, verify_email_get, reset_password_post, \
    reset_password_get, VerifyEmailViewSet, ResetPasswordViewSet
from .settings import SettingsViewSet

router = routers.DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'ingredients', IngredientViewSet, basename='Ingredient')
router.register(r'school_items', SchoolMealItemsViewSet, basename='SchoolMealItems')
router.register(r'meals', MealSelectionViewSet, basename='MealSelection')
router.register(r'settings', SettingsViewSet, basename='Settings')

router.register(r'nutritional_requirements', NutritionalRequirementsViewSet, basename='NutritionalRequirements')
router.register(r'suggest', SuggestViewSet, basename='SuggestViewSet')

router.register(r'verify_email', VerifyEmailViewSet, basename='VerifyEmail')
router.register(r'reset_password', ResetPasswordViewSet, basename='ResetPassword')

print(router.get_urls())

urlpatterns = [
    # Authentication
    path('token_auth/', obtain_auth_token),
    path('auth/', include('rest_framework.urls')),
    path('register/', register_student_view, name='register_student'),
    path('register/check_email/<str:email>/', check_email_view, name='check_email'),

    # TODO: Password reset and confirmation

    # Endpoints
    path('analytics/', include('backend.views.api.analytics')),
    path('', include(router.urls)),
]
