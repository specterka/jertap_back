from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from users.managers import UserManager, OTPManager


# Create your models here.

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created`` and ``modified`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def profile_pic_dir(instance, filename):
    return f'UserProfile/{instance.id}_{filename}'


AUTH_PROVIDERS = {
    'facebook': 'facebook', 'google': 'google', 'credentials': 'credentials'
}


class User(TimeStampedModel, DirtyFieldsMixin, AbstractBaseUser, PermissionsMixin):
    auth_provider = models.CharField(max_length=255, default=AUTH_PROVIDERS.get('credentials'))
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, )
    mobile_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    profile_image = models.ImageField(blank=True, null=True, upload_to=profile_pic_dir)
    date_of_birth = models.DateField(null=True, blank=True)
    is_visitor = models.BooleanField(default=False)
    is_cafe_owner = models.BooleanField(default=False)
    is_cafe_manager = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(max_length=255, null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['mobile_number']),
        ]

    def __str__(self):
        return self.username if self.username else ''

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    @property
    def following_count(self):
        return self.user_following.all().count() - self.user_following.filter(is_approved=False).count()

    @property
    def follower_count(self):
        return self.user_followers.all().count() - self.user_followers.filter(is_approved=False).count()

    @property
    def request_count(self):
        return self.user_followers.filter(is_approved=False).count()

    @property
    def participated_count(self):
        return self.participated.all().count()


class PasswordResetConfirmation(models.Model):
    user = models.OneToOneField(User, primary_key=True,
                                on_delete=models.CASCADE, related_name="pass_reset_confirmation")
    code = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    objects = OTPManager()

    def __str__(self):
        return self.user.username + ' --> ' + str(self.code)


class TwoFactorVerificationOTP(TimeStampedModel):
    user = models.ForeignKey(User, related_name='two_factor_otp', on_delete=models.CASCADE)
    code = models.BigIntegerField(unique=True)

    objects = OTPManager()

    def __str__(self):
        return self.user.username + ' --> ' + str(self.code)


def collaborator_profile_pic_dir(instance, filename):
    return f'CollaboratorProfile/{instance.id}_{filename}'


class Collaborator(TimeStampedModel):
    full_name = models.CharField(max_length=255)
    profile_pic = models.ImageField(blank=True, null=True, upload_to=collaborator_profile_pic_dir)
    description = models.TextField(blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    youtube_channel_link = models.TextField(blank=True, null=True)
    fb_profile_link = models.TextField(blank=True, null=True)
    insta_profile_link = models.TextField(blank=True, null=True)
    twitter_profile_link = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
