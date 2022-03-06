from django.contrib import admin

from .models import LogTextFeedback, LogSurvey, LogMealItemVote, LogMealChoice, Ingredient, MealItem, School, \
    SchoolProfile, StudentProfile, MealSelection


# Register your models here.

@admin.register(School, site=admin.site)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


admin.site.register(SchoolProfile)


@admin.register(StudentProfile, site=admin.site)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'school')
    list_display_links = ('name',)
    list_filter = ('school',)
    ordering = ('name',)
    search_fields = ('name',)

    def user_id(self, obj):
        return obj.user.id


@admin.register(MealSelection, site=admin.site)
class MealSelectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'timestamp', 'item_count', 'school')
    list_display_links = ('name',)
    list_filter = ('school', 'group')
    ordering = ('timestamp',)
    search_fields = ('name', 'group')

    def item_count(self, obj):
        return obj.items.count()


@admin.register(MealItem, site=admin.site)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'station', 'category', 'school')
    list_display_links = ('name',)
    list_filter = ('school', 'station', 'category')
    ordering = ('station', 'name')
    search_fields = ('name', 'station')


admin.site.register(Ingredient)


@admin.register(LogMealChoice, site=admin.site)
class LogMealChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_name', 'profile_email', 'meal', 'timestamp')
    list_display_links = ('profile_email',)
    list_filter = ('meal',)
    ordering = ('meal',)
    search_fields = ('profile_name', 'profile_email', 'meal')

    def profile_name(self, obj):
        return obj.profile.name

    def profile_email(self, obj):
        return obj.profile.user.username


admin.site.register(LogMealItemVote)
admin.site.register(LogSurvey)


@admin.register(LogTextFeedback, site=admin.site)
class LogTextFeedbackAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'feedback_short')

    def feedback_short(self, obj):
        if len(obj.feedback) > 50:
            return obj.feedback[:50] + '...'
        else:
            return obj.feedback
