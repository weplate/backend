from django.urls import path
from .info import schools, ingredients, meals, items
from .meal_planning import nutritional_requirements

urlpatterns = [
    path('schools/', schools, name='schools'),
    path('ingredients/', ingredients, name='ingredients'),
    path('meals/', meals, name='meals'),
    path('items/<int:meal_id>/', items, name='items'),

    path('nutritional_requirements/', nutritional_requirements, name='nutritional_requirements'),
]
