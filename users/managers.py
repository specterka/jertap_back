from random import randint

from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager

class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class OTPManager(Manager):
    def generate(self, **kwargs):
        code = randint(100000, 999999)
        return self.create(code=code, **kwargs)