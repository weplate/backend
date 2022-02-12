from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .info import SchoolViewSet, IngredientViewSet, MealSelectionViewSet, SchoolMealItemsViewSet
from .meal_planning import NutritionalRequirementsViewSet

router = routers.DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'ingredients', IngredientViewSet, basename='Ingredient')
router.register(r'items', SchoolMealItemsViewSet, basename='SchoolMealItems')
router.register(r'meals', MealSelectionViewSet, basename='MealSelection')
router.register(r'nutritional_requirements', NutritionalRequirementsViewSet, basename='NutritionalRequirements'),

urlpatterns = [
    path('token-auth/', obtain_auth_token),
    path('auth/', include('rest_framework.urls')),

    path('', include(router.urls)),
]
# urlpatterns = [
#     path('ingredients/', ingredients, name='ingredients'),
#     path('meals/', meals, name='meals'),
#     path('school_items/', school_items, name='school_items'),
#     path('items/<int:meal_id>/', items, name='items'),
#
# ]
