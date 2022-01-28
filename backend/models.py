from django.db import models
from django.contrib.auth.models import User
from collections import namedtuple


# Create your models here.
class NutritionalInfo:
    PropertyInfo = namedtuple('PropertyInfo', 'displayname unit default')

    units = {
        'ug': 10**-6,
        'mg': 10**-3,
        'g': 1.,
        'kg': 1000.,
    }

    @classmethod
    def convert_unit(cls, value, f, t):
        if f not in cls.units: raise ValueError(f'Invalid Unit {f}')
        if t not in cls.units: raise ValueError(f'Invalid Unit {t}')

        return value * (cls.units[f] / cls.units[t])

    nutrients = {
        'calories': PropertyInfo('Calories (cal)', 'g', 0)  # I know calories is not in grams, but no conversions need to be done anyway, so this should be ok
    }

    def __init__(self, obj={}):
        """
        :param obj: Construct this from JSON
        """
        pass

    def json(self):
        pass

class MealOption(models.Model):
    pass

class MealSelection(models.Model):
    pass

class School(models.Model):
    pass

class Profile(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
