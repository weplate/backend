from django.urls import path
from .info import schools

urlpatterns = [
    path('schools/', schools, name='schools')
]
