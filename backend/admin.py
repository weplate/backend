from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.School)
admin.site.register(models.SchoolProfile)
admin.site.register(models.StudentProfile)

admin.site.register(models.MealSelection)
admin.site.register(models.MealItem)
admin.site.register(models.Ingredient)
admin.site.register(models.NutritionalInfo)

admin.site.register(models.LogMealItemSwitch)
admin.site.register(models.LogMeal)
admin.site.register(models.LogUsageAnalytics)
