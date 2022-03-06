from django.db import models

from backend.models.meal import MealSelection, MealItem
from backend.models.profile import StudentProfile


class LogMealChoice(models.Model):
    # Basic info about who/when
    profile = models.ForeignKey(to=StudentProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    # what meal/items is this tied to?
    meal = models.ForeignKey(to=MealSelection, on_delete=models.SET_NULL, null=True)
    small1 = models.ForeignKey(to=MealItem, on_delete=models.SET_NULL, null=True, related_name='meal_item_small_1')
    small2 = models.ForeignKey(to=MealItem, on_delete=models.SET_NULL, null=True, related_name='meal_item_small_2')
    large = models.ForeignKey(to=MealItem, on_delete=models.SET_NULL, null=True, related_name='meal_item_large')
    small1_portion = models.FloatField(verbose_name='Section A Size (mL)')
    small2_portion = models.FloatField(verbose_name='Section B Size (mL)')
    large_portion = models.FloatField(verbose_name='Section C Size (mL)')


class LogMealItemVote(models.Model):
    # Basic info about who/when
    profile = models.ForeignKey(to=StudentProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    # Info
    meal_item = models.ForeignKey(to=MealItem, on_delete=models.SET_NULL, null=True)
    liked = models.BooleanField(verbose_name='Liked (True/False)')


class LogTextFeedback(models.Model):
    timestamp = models.DateTimeField()
    feedback = models.CharField(max_length=512, verbose_name='Feedback')


class LogSurvey(models.Model):
    # Basic info about who/when
    profile = models.ForeignKey(to=StudentProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()  # When was the log reported
    track_duration = models.DurationField()  # How long was the logging period

    # TODO: what are we going to track