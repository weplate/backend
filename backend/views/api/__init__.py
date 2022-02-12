from django.urls import path
from .info import schools, ingredients, meals, items

urlpatterns = [
    path('schools/', schools, name='schools'),
    path('ingredients/', ingredients, name='ingredients'),
    path('meals/', meals, name='meals'),
    path('items/<meal_id:int>/', items, name='items'),
]
