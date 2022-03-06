from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .auth import verify_email_get, verify_email_post, reset_password_get, reset_password_post
from .info import SchoolViewSet, IngredientViewSet, MealSelectionViewSet, SchoolMealItemsViewSet
from .meal_planning import NutritionalRequirementsViewSet, SuggestViewSet
from .register import register_student_view, check_email_view
from .settings import SettingsViewSet

router = routers.DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'ingredients', IngredientViewSet, basename='Ingredient')
router.register(r'school_items', SchoolMealItemsViewSet, basename='SchoolMealItems')
router.register(r'meals', MealSelectionViewSet, basename='MealSelection')
router.register(r'settings', SettingsViewSet, basename='Settings')

router.register(r'nutritional_requirements', NutritionalRequirementsViewSet, basename='NutritionalRequirements')
router.register(r'suggest', SuggestViewSet, basename='SuggestViewSet')

urlpatterns = [
    # Authentication
    path('token_auth/', obtain_auth_token),
    path('auth/', include('rest_framework.urls')),
    path('register/', register_student_view, name='register_student'),
    path('register/check_email/<str:email>/', check_email_view, name='check_email'),
    path('verify_email/<int:user_id>/<str:token>/', verify_email_get, name='verify_email_get'),
    path('verify_email/', verify_email_post, name='verify_email_post'),
    path('reset_password/<int:user_id>/<str:token>/', reset_password_get, name='reset_password_get'),
    path('reset_password/', reset_password_post, name='reset_password_post'),

    # TODO: Password reset and confirmation

    # Endpoints
    path('analytics/', include('backend.views.api.analytics')),
    path('', include(router.urls)),
]
