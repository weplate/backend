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


class Ingredient(models.Model):
    name = models.CharField(max_length=64)
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class MealItem(models.Model):
    name = models.CharField(max_length=64)
    station = models.CharField(max_length=64)
    graphic = models.FileField(upload_to=MEAL_ITEM_GRAPHICS, null=True, blank=True)

    VEGETABLE = 'vegetable'
    PROTEIN = 'protein'
    GRAINS = 'grain'
    CATEGORIES = (
        (VEGETABLE, 'Vegetable'),
        (PROTEIN, 'Protein'),
        (GRAINS, 'Grains')
    )

    category = models.CharField(max_length=32, choices=CATEGORIES, null=True, blank=True)
    cafeteria_id = models.CharField(max_length=32, null=True, blank=True)

    # Ingredients, nutrition, other numbers
    portion_weight = models.FloatField(verbose_name='Portion Weight (g)')
    portion_volume = models.FloatField(verbose_name='Portion Volume (ml)')
    max_pieces = models.IntegerField(verbose_name='Max # of Pieces', default=10)
    ingredients = models.ManyToManyField(to=Ingredient, blank=True)

    # School it belongs to
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

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

    # Returns in g/ml
    def density(self):
        return self.portion_weight / self.portion_volume

    def __str__(self):
        return f'{self.name} @ {self.station} (ID: {self.id})'


class MealSelection(models.Model):
    name = models.CharField(max_length=64)
    group = models.CharField(max_length=64, default='default')
    timestamp = models.DateTimeField()
    items = models.ManyToManyField(to=MealItem)

    # School it belongs to
    school = models.ForeignKey(to=School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name