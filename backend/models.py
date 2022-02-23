from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

MEAL_ITEM_GRAPHICS = 'assets/meal_items/'


class School(models.Model):
    name = models.CharField(max_length=64, unique=True)

    @property
    def meals(self):
        return MealSelection.objects.get(school=self)

    @property
    def meal_items(self):
        return MealItem.objects.get(school=self)

    def __str__(self):
        return self.name


class NutritionalInfo(models.Model):
    name = models.CharField(max_length=64, default='No Name')

    # Macronutrients
    calories = models.FloatField(verbose_name='Calories (cal)', default=0)
    carbohydrate = models.FloatField(verbose_name='Carbohydrates (g)', default=0)
    protein = models.FloatField(verbose_name='Protein (g)', default=0)
    total_fat = models.FloatField(verbose_name='Total Fat (g)', default=0)
    saturated_fat = models.FloatField(verbose_name='Saturated Fat (g)', default=0)
    trans_fat = models.FloatField(verbose_name='Trans Fat (g)', default=0)

    # Micronutrients
    sugar = models.FloatField(verbose_name='Sugar (g)', default=0)
    cholesterol = models.FloatField(verbose_name='Cholesterol (mg)', default=0)
    fiber = models.FloatField(verbose_name='Dietary Fiber (g)', default=0)
    sodium = models.FloatField(verbose_name='Sodium (mg)', default=0)
    potassium = models.FloatField(verbose_name='Potassium (mg)', default=0)
    calcium = models.FloatField(verbose_name='Calcium (mg)', default=0)
    iron = models.FloatField(verbose_name='Iron (mg)', default=0)

    vitamin_d = models.FloatField(verbose_name='Vitamin D (IU)', default=0)
    vitamin_c = models.FloatField(verbose_name='Vitamin C (mg)', default=0)
    vitamin_a = models.FloatField(verbose_name='Vitamin A (RE)', default=0)

    def __str__(self):
        return f'Info {self.name} for {self.mealitem_set.name} (calories: {self.calories})'


class Ingredient(models.Model):
    name = models.CharField(max_length=64)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} @ {self.school.name}'


class MealItem(models.Model):
    name = models.CharField(max_length=64)
    station = models.CharField(max_length=64)
    graphic = models.FileField(upload_to=MEAL_ITEM_GRAPHICS, null=True)

    # Ingredients, nutrition, other numbers
    portion_weight = models.FloatField(verbose_name='Portion Weight (g)')
    portion_volume = models.FloatField(verbose_name='Portion Volume (ml)')
    nutrition = models.ForeignKey(to=NutritionalInfo, on_delete=models.SET_NULL, null=True)
    ingredients = models.ManyToManyField(to=Ingredient)

    # School it belongs to
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

    # Returns in g/ml
    def density(self):
        return self.portion_weight / self.portion_volume

    def __str__(self):
        return f'{self.name} @ station {self.station} @ {self.school.name}'


class MealSelection(models.Model):
    name = models.CharField(max_length=64)
    group = models.CharField(max_length=64, default='default')
    timestamp = models.DateTimeField()
    items = models.ManyToManyField(to=MealItem)

    # School it belongs to
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} (group: {self.group}) @ {self.timestamp.isoformat()} @ {self.school.name}'


class StudentProfile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

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

    MILD = 'mild'
    MODERATE = 'moderate'
    HEAVY = 'heavy'
    EXTREME = 'extreme'

    ACTIVITY_LEVELS = [
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
        return f'{self.name} @ {self.school.name} (Email: {self.user.username})'


class SchoolProfile(models.Model):
    name = models.CharField(max_length=64)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)


# Analytics
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
