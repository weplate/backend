from django.urls import path, include
from .auth import view_login, view_logout

urlpatterns = [
    path('login/', view_login, name='login'),
    path('logout/', view_logout, name='logout')
]
