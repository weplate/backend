from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .info import SchoolViewSet, IngredientViewSet, MealSelectionViewSet, SchoolMealItemsViewSet
from .meal_planning import NutritionalRequirementsViewSet
from .settings import SettingsViewSet

router = routers.DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'ingredients', IngredientViewSet, basename='Ingredient')
router.register(r'school_items', SchoolMealItemsViewSet, basename='SchoolMealItems')
router.register(r'meals', MealSelectionViewSet, basename='MealSelection')
router.register(r'nutritional_requirements', NutritionalRequirementsViewSet, basename='NutritionalRequirements'),
router.register(r'settings', SettingsViewSet, basename='Settings')

urlpatterns = [
    path('token_auth/', obtain_auth_token),
    path('auth/', include('rest_framework.urls')),

    path('', include(router.urls)),
]
