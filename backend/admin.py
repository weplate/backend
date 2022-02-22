from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.School)
admin.site.register(models.SchoolProfile)
admin.site.register(models.StudentProfile)

admin.site.register(models.MealSelection)


@admin.register(models.MealItem, site=admin.site)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'station', 'school')
    list_display_links = ('name',)
    list_filter = ('school', 'station')


admin.site.register(models.Ingredient)
admin.site.register(models.NutritionalInfo)

admin.site.register(models.LogMealChoice)
admin.site.register(models.LogMealItemVote)
admin.site.register(models.LogSurvey)
admin.site.register(models.LogTextFeedback)
