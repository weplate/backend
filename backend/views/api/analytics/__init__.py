from django.urls import path, include
from rest_framework import routers

from backend.models import LogMealChoice, LogMealItemVote
from backend.views.api.analytics.meals import create_user_log_viewset

router = routers.DefaultRouter()
router.register(r'meal_choice', create_user_log_viewset(LogMealChoice), basename='LogMealChoice')
router.register(r'meal_item_vote', create_user_log_viewset(LogMealItemVote), basename='LogMealItemVote')

urlpatterns = [
    path('', include(router.urls))
]
