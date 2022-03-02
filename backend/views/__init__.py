from django.urls import path, include

from backend.views.data_admin import data_admin_view, debug_view

urlpatterns = [
    path('', debug_view, name='root_debug_view'),

    # path('login/', view_login, name='login'), # TODO: School admin login/logout, iteration 2
    # path('logout/', view_logout, name='logout'),

    path('data_admin/', include('backend.views.data_admin')),
    path('api/', include('backend.views.api')),
    path('jobs/', include('backend.views.jobs')),
]
