from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .info import SchoolViewSet, IngredientViewSet, MealSelectionViewSet, SchoolMealItemsViewSet, VersionViewSet
from .item_image import ItemImageViewSet
from .meal_planning import NutritionalRequirementsViewSet, SuggestViewSet
from .auth import register_student_view, check_email_view, VerifyEmailViewSet, ResetPasswordViewSet
from .settings import SettingsViewSet

router = routers.DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'ingredients', IngredientViewSet, basename='Ingredient')
router.register(r'school_items', SchoolMealItemsViewSet, basename='SchoolMealItems')
router.register(r'meals', MealSelectionViewSet, basename='MealSelection')
router.register(r'version', VersionViewSet, basename='Version')
router.register(r'settings', SettingsViewSet, basename='Settings')

router.register(r'nutritional_requirements', NutritionalRequirementsViewSet, basename='NutritionalRequirements')
router.register(r'suggest', SuggestViewSet, basename='SuggestViewSet')

router.register(r'item_image', ItemImageViewSet, basename='ItemImageViewSet')

router.register(r'verify_email', VerifyEmailViewSet, basename='VerifyEmail')
router.register(r'reset_password', ResetPasswordViewSet, basename='ResetPassword')

urlpatterns = [
    # Authentication
    path('token_auth/', obtain_auth_token),
    path('auth/', include('rest_framework.urls')),
    path('register/', register_student_view, name='register_student'),
    path('register/check_email/<str:email>/', check_email_view, name='check_email'),

    # TODO: Password reset and confirmation

    # Endpoints
    path('analytics/', include('backend.views.api.analytics')),
    path('notification/', include('backend.views.api.notification')),
    path('', include(router.urls)),
]
