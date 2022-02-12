from django.urls import path
from .info import schools, ingredients, meals, items, school_items
from .meal_planning import nutritional_requirements

urlpatterns = [
    path('schools/', schools, name='schools'),
    path('ingredients/', ingredients, name='ingredients'),
    path('meals/', meals, name='meals'),
    path('school_items/', school_items, name='school_items'),
    path('items/<int:meal_id>/', items, name='items'),

    path('nutritional_requirements/', nutritional_requirements, name='nutritional_requirements'),
]
