from django.db import models
from django.contrib.auth.models import User

MEAL_ITEM_GRAPHICS = 'assets/meal_items/'


class School(models.Model):
    name = models.CharField(max_length=64, unique=True)

    @property
    def meals(self):
        return MealSelection.objects.get(school=self)

    @property
    def meal_items(self):
        return MealItem.objects.get(school=self)


class NutritionalInfo(models.Model):
    name = models.CharField(max_length=64, unique=True)

    # Macronutrients
    calories = models.FloatField(verbose_name='Calories (cal)', default=0)
    protein = models.FloatField(verbose_name='Protein (g)', default=0)
    fat = models.FloatField(verbose_name='Protein (g)', default=0)

    # Micronutrients
    sugar = models.FloatField(verbose_name='Sugar (g)', default=0)
    cholesterol = models.FloatField(verbose_name='Cholesterol (mg)', default=0)
    fiber = models.FloatField(verbose_name='Dietary Fiber (g)', default=0)
    sodium = models.FloatField(verbose_name='Sodium (mg)', default=0)
    potassium = models.FloatField(verbose_name='Potassium (mg)', default=0)
    calcium = models.FloatField(verbose_name='Calcium (mg)', default=0)
    iron = models.FloatField(verbose_name='Iron (mg)', default=0)

    vitamin_d = models.FloatField(verbose_name='Vitamin D (%)', default=0)
    vitamin_c = models.FloatField(verbose_name='Vitamin C (%)', default=0)
    vitamin_a = models.FloatField(verbose_name='Vitamin A (%)', default=0)


class Ingredient(models.Model):
    name = models.CharField(max_length=64)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)


class MealItem(models.Model):
    name = models.CharField(max_length=64, unique=True)
    graphic = models.FileField(upload_to=MEAL_ITEM_GRAPHICS, null=True)

    # Ingredients stuff
    nutrition = models.ForeignKey(to=NutritionalInfo, on_delete=models.SET_NULL, null=True)
    ingredients = models.ManyToManyField(to=Ingredient)

    # School it belongs to
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)


class MealSelection(models.Model):
    name = models.CharField(max_length=64, unique=True)
    group = models.CharField(max_length=64, default='default')
    timestamp = models.DateTimeField()
    items = models.ManyToManyField(to=MealItem)

    # School it belongs to
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)


class StudentProfile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

    # Personal details/preferences
    name = models.CharField(max_length=256)

    # Biological Information and Diet Plan
    height = models.FloatField(verbose_name='Height (m)')
    age = models.IntegerField(verbose_name='Age (years)')
    weight = models.FloatField(verbose_name='Weight (kg)')

    # Choice stuff
    LOSE_WEIGHT = 'lose_weight'
    BUILD_MUSCLE = 'build_muscle'
    ATHLETIC_PERFORMANCE = 'athletic_performance'
    BODY_RECOMPOSITION = 'body_recomposition'
    IMPROVE_HEALTH = 'improve_health'

    HEALTH_GOALS = [
        (LOSE_WEIGHT, 'Lose Weight'),
        (BUILD_MUSCLE, 'Build Muscle'),
        (ATHLETIC_PERFORMANCE, 'Athletic Performance'),
        (BODY_RECOMPOSITION, 'Body Recomposition'),
        (IMPROVE_HEALTH, 'Improve Health')
    ]

    MALE = 'male'
    FEMALE = 'female'

    SEXES = [
        (MALE, 'Male'),
        (FEMALE, 'Female')
    ]

    sex = models.CharField(max_length=64, verbose_name='Sex', choices=SEXES)
    health_goal = models.CharField(max_length=64, verbose_name='Health Goal', choices=HEALTH_GOALS)

    # banning/favouring meal items
    ban = models.ManyToManyField(to=MealItem, related_name='ban')
    favour = models.ManyToManyField(to=MealItem, related_name='favour')
    allergies = models.ManyToManyField(to=Ingredient)


class SchoolProfile(models.Model):
    name = models.CharField(max_length=64)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)


# Analytics
class LogMealItemSwitch(models.Model):
    item_from = models.ForeignKey(to=MealItem, on_delete=models.CASCADE, related_name='item_from')
    item_to = models.ForeignKey(to=MealItem, on_delete=models.CASCADE, related_name='item_to')


# TODO: Make this name better
class LogMeal(models.Model):
    # Basic info about who/when
    profile = models.ForeignKey(to=StudentProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    # what meal/items is this tied to?
    meal = models.ForeignKey(to=MealSelection, on_delete=models.SET_NULL, null=True)
    meal_items = models.ManyToManyField(to=MealItem)

    # review of app
    switches = models.ManyToManyField(to=LogMealItemSwitch)
    liked = models.BooleanField()
    used_weplate = models.BooleanField()


class LogUsageAnalytics(models.Model):
    # Basic info about who/when
    profile = models.ForeignKey(to=StudentProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()  # When was the log reported
    track_duration = models.DurationField()  # How long was the logging period

    # TODO: what are we going to track
