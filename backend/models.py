from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string

from backend.common import fetch_or_none


class TokenManager(models.Manager):
    def create_token(self, user: User, valid_for=timedelta(minutes=10), **kwargs):
        """
        Creates an expiring token (along with necessary additional parameters) while overwriting previous
        tokens for the assigned user and returns the object
        """

        obj = fetch_or_none(self.model, user=user)
        if obj is None:
            obj = self.model(user=user, expire_at=datetime.now() + valid_for, **kwargs)
        obj.token = get_random_string(length=32, allowed_chars='0123456789abcdef')
        obj.save()

        return obj

    def get_token(self, user: User):
        """
        Fetches a token DB object for the given user.  If expired or non-existent, None will be returned.
        This operation is mutating- expired tokens will be deleted
        """

        obj = fetch_or_none(self.model, user=user)
        if obj:
            if obj.expire_at > datetime.now():
                obj.delete()
                return None
            else:
                return obj
        else:
            return None


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
