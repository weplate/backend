from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from backend.models.meal import School, MealItem, Ingredient


class StudentProfile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)
    is_verified = models.BooleanField()

    # Personal details/preferences
    name = models.CharField(max_length=256)

    # Biological Information and Diet Plan
    height = models.FloatField(verbose_name='Height (cm)')
    weight = models.FloatField(verbose_name='Weight (kg)')
    birthdate = models.DateField(verbose_name='Birthdate')
    meals = models.JSONField(verbose_name='Meals Eaten')
    meal_length = models.FloatField(verbose_name='Meal Length (minutes)')

    # Choice stuff
    LOSE_WEIGHT = 'lose_weight'
    BUILD_MUSCLE = 'build_muscle'
    ATHLETIC_PERFORMANCE = 'athletic_performance'
    IMPROVE_TONE = 'improve_tone'
    IMPROVE_HEALTH = 'improve_health'

    HEALTH_GOALS = [
        (LOSE_WEIGHT, 'Lose Weight'),
        (BUILD_MUSCLE, 'Build Muscle'),
        (ATHLETIC_PERFORMANCE, 'Athletic Performance'),
        (IMPROVE_TONE, 'Improve Body Tone'),
        (IMPROVE_HEALTH, 'Improve Health')
    ]

    MALE = 'male'
    FEMALE = 'female'

    SEXES = [
        (MALE, 'Male'),
        (FEMALE, 'Female')
    ]

    SEDENTARY = 'sedentary'
    MILD = 'mild'
    MODERATE = 'moderate'
    HEAVY = 'heavy'
    EXTREME = 'extreme'

    ACTIVITY_LEVELS = [
        (SEDENTARY, 'Sedentary'),
        (MILD, 'Mild Activity'),
        (MODERATE, 'Moderate Activity'),
        (HEAVY, 'Heavy or Labour Intensive Activity'),
        (EXTREME, 'Extreme Activity')
    ]

    # This one will be written differently since it's not "really" a choicefield
    BREAKFAST = 'breakfast'
    MORN_SNACK = 'morning_snack'
    LUNCH = 'lunch'
    AFT_SNACK = 'afternoon_snack'
    DINNER = 'dinner'
    EVE_SNACK = 'evening_snack'

    MEALS = [
        (BREAKFAST, 'Breakfast'),
        (MORN_SNACK, 'Morning Snack'),
        (LUNCH, 'Lunch'),
        (AFT_SNACK, 'Afternoon Snack'),
        (DINNER, 'Dinner'),
        (EVE_SNACK, 'Evening Snack')
    ]

    sex = models.CharField(max_length=64, verbose_name='Sex', choices=SEXES)
    health_goal = models.CharField(max_length=64, verbose_name='Health Goal', choices=HEALTH_GOALS)
    activity_level = models.CharField(max_length=64, verbose_name='Activity Level', choices=ACTIVITY_LEVELS)

    grad_year = models.IntegerField()

    @staticmethod
    def _valid_option(opt_list, opt):
        return any((opt == opt_key for opt_key, opt_name in opt_list))

    @classmethod
    def valid_sex(cls, o):
        return StudentProfile._valid_option(cls.SEXES, o)

    @classmethod
    def valid_health_goal(cls, o):
        return StudentProfile._valid_option(cls.HEALTH_GOALS, o)

    @classmethod
    def valid_activity_level(cls, o):
        return StudentProfile._valid_option(cls.ACTIVITY_LEVELS, o)

    @classmethod
    def valid_meal(cls, o):
        return StudentProfile._valid_option(cls.MEALS, o)

    # banning/favouring meal items
    ban = models.ManyToManyField(to=MealItem, related_name='ban', blank=True)
    favour = models.ManyToManyField(to=MealItem, related_name='favour', blank=True)
    allergies = models.ManyToManyField(to=Ingredient, blank=True)

    def clean(self):
        super().clean()
        for meal in self.meals:
            if not StudentProfile.valid_meal(meal):
                raise ValidationError({'meal': f'Value \'{meal}\' is not a valid choice.'})

    def __str__(self):
        return f'{self.name} @ {self.school.name} (Email: {self.user.username}, Id: {self.id})'


class SchoolProfile(models.Model):
    name = models.CharField(max_length=64)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)