from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from rest_framework.exceptions import APIException

from backend.utils import fetch_or_none

import pytz


class TokenManager(models.Manager):
    def create_token(self, user: User, valid_for=timedelta(minutes=10), **kwargs):
        """
        Creates an expiring token (along with necessary additional parameters) while overwriting previous
        tokens for the assigned user and returns the object
        """

        obj = fetch_or_none(self.model, user=user)
        if obj is None:
            obj = self.model()

        obj.user = user
        obj.expire_at = pytz.utc.localize(datetime.now() + valid_for)
        obj.token = get_random_string(length=32, allowed_chars='0123456789abcdef')
        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.save()

        return obj

    def get_token(self, user: User):
        """
        Fetches a token DB object for the given user.  If expired or non-existent, None will be returned.
        This operation is mutating- expired tokens will be deleted
        """

        obj = fetch_or_none(self.model, user=user)
        if obj:
            print(f'{obj.expire_at=} {pytz.utc.localize(datetime.now())=}')
            if obj.expire_at < pytz.utc.localize(datetime.now()):
                obj.delete()
                return None
            else:
                return obj
        else:
            return None

    def process_token(self, user: User, token_str: str):
        """
        Similar to get_token, but the token corresponding to the user is 'processed', meaning that it's checked for
        correctness and then deleted from the database if it's correct

        APIException will be thrown if the token is incorrect or non-existant
        """

        token_obj = self.get_token(user)
        if token_obj:
            if token_obj.token != token_str:
                raise APIException('Invalid/incorrect token')
            else:
                token_obj.delete()
                return token_obj
        else:
            raise APIException('No token found/token expired')


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)
    expire_at = models.DateTimeField()

    objects = TokenManager()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)
    new_password = models.CharField(max_length=256)  # No way it's longer than this
    expire_at = models.DateTimeField()

    objects = TokenManager()
