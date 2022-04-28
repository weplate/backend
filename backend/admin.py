from typing import Type

from django import forms
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db import models

from .models import LogTextFeedback, LogSurvey, LogMealItemVote, LogMealChoice, Ingredient, MealItem, School, \
    StudentProfile, MealSelection, ImageQueueEntry


# Register your models here.


def filter_by_school_perms(user, queryset):
    school_ids = [int(perm.split('.')[-1]) for perm in user.get_all_permissions() if 'admin_school' in perm]
    return queryset.filter(school__id__in=school_ids)


# https://stackoverflow.com/questions/22968631/how-to-filter-filter-horizontal-in-django-admin
def school_account_admin_class(model_cls: Type[models.Model], fields_to_change: list[str]):
    """
    Returns a class that subclasses ModelAdmin and limits viewable objects to only within the school an account belongs to
    @param model_cls The class that the class will be superclassing.  Required for smoe of the class definition
    @param fields_to_change A list of fields (expected to be foreignkey-like fields) whose available choices should be limited to being in-school.  If this field is empty, then the admin form sill not be modified
    @returns The class
    """

    class SchoolAccountAdmin(admin.ModelAdmin):
        def has_view_or_change_permission(self, request: WSGIRequest, obj=None):
            if obj and not request.user.has_perm(f'backend.admin_school.{obj.school.id}'):
                return False

            return super().has_view_or_change_permission(request, obj)

        def get_queryset(self, request: WSGIRequest):
            queryset = super().get_queryset(request)
            if request.user.is_superuser:
                return queryset
            return filter_by_school_perms(request.user, queryset)

        def get_form(self, request, obj=None, change=False, **kwargs):
            form = super().get_form(request, obj, change, **kwargs)
            if request.user.is_superuser or not fields_to_change:
                return form

            class ModelFormClass(form):
                class Meta:
                    model = model_cls
                    exclude = []

                def __init__(self, *i_args, **i_kwargs):
                    super().__init__(*i_args, **i_kwargs)

                    self.user = None
                    for field in fields_to_change:
                        self.fields[field].queryset = filter_by_school_perms(request.user, self.fields[field].queryset)

            return ModelFormClass

    return SchoolAccountAdmin


@admin.register(School, site=admin.site)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


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
class MealSelectionAdmin(school_account_admin_class(MealSelection, ['items'])):
    list_display = ('id', 'name', 'group', 'timestamp', 'item_count', 'school')
    list_display_links = ('name',)
    list_filter = ('school', 'group')
    ordering = ('timestamp',)
    search_fields = ('name', 'group')

    filter_horizontal = ('items',)

    def item_count(self, obj):
        return obj.items.count()


@admin.register(MealItem, site=admin.site)
class MealItemAdmin(school_account_admin_class(MealItem, ['ingredients'])):
    list_display = ('id', 'name', 'station', 'category', 'school')
    list_display_links = ('name',)
    list_filter = ('school', 'station', 'category')
    ordering = ('station', 'name')
    search_fields = ('name', 'station', 'cafeteria_id')

    filter_horizontal = ('ingredients',)


@admin.register(Ingredient, site=admin.site)
class IngredientAdmin(school_account_admin_class(Ingredient, [])):
    list_display = ('id', 'name', 'school')
    list_display_links = ('name',)
    list_filter = ('school',)
    ordering = ('school', 'name')
    search_fields = ('name',)


@admin.register(ImageQueueEntry, site=admin.site)
class ImageQueueEntryAdmin(admin.ModelAdmin):
    list_display = ('item', 'profile', 'timestamp')
    list_display_links = ('item',)
    ordering = ('timestamp',)
    search_fields = ('item', 'profile')


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


@admin.register(LogMealItemVote, site=admin.site)
class LogMealItemVoteAdmin(admin.ModelAdmin):
    pass


@admin.register(LogSurvey, site=admin.site)
class LogSurveyAdmin(admin.ModelAdmin):
    pass


@admin.register(LogTextFeedback, site=admin.site)
class LogTextFeedbackAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'feedback_short')

    def feedback_short(self, obj):
        if len(obj.feedback) > 50:
            return obj.feedback[:50] + '...'
        else:
            return obj.feedback
