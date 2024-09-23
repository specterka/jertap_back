import random
from datetime import timedelta
from django.contrib.auth import authenticate, password_validation
from django.core import exceptions
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from google.auth.transport import requests
from google.oauth2 import id_token
import facebook
from rest_framework.exceptions import AuthenticationFailed
from jertap_backend.settings import GOOGLE_CLIENT_ID, SOCIAL_SECRET, PASS_REST_CONFIRM_EXPIRE_MINUTE, VERIFICATION_CODE_EXPIRE_MINUTE
from users.models import User, PasswordResetConfirmation, TwoFactorVerificationOTP


def get_object_or_none(model_class, **kwargs):
    """Identical to get_object_or_404, except instead of returning Http404,
    this returns None.
    """
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        return None


def generate_username(name):
    username = "_".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + '_' + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider and filtered_user_by_email[0].is_visitor:

            registered_user = authenticate(
                email=email, password=SOCIAL_SECRET)

            return {
                'username': registered_user.username,
                'email': registered_user.email,
                'tokens': registered_user.tokens()}

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        user = {
            'username': generate_username(name), 'email': email, 'is_visitor': True,
            'password': SOCIAL_SECRET}
        user = User.objects.create_user(**user)
        user.auth_provider = provider
        user.save()

        new_user = authenticate(
            email=email, password=SOCIAL_SECRET)
        return {
            'email': new_user.email,
            'username': new_user.username,
            'tokens': new_user.tokens()
        }


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token, requests.Request())

            if 'accounts.google.com' in idinfo['iss']:
                return idinfo

        except:
            return "The token is either invalid or has expired"


class Facebook:
    """
    Facebook class to fetch the user info and return it
    """

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the facebook GraphAPI to fetch the user info
        """
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request('/me?fields=name,email')
            return profile
        except:
            return "The token is invalid or expired."


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        if user_data['aud'] != GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('oops, who are you?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name)


class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)

        try:
            user_id = user_data['id']
            email = user_data['email']
            name = user_data['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                user_id=user_id,
                email=email,
                name=name
            )
        except Exception as identifier:

            raise serializers.ValidationError(
                'The token  is invalid or expired. Please login again.'
            )


class ManualRegistrationSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=True, max_length=255)
    email = serializers.EmailField(required=True, max_length=255)
    mobile_number = serializers.CharField(required=True, max_length=20)

    # class Meta:
    #     model = User
    #     fields = ['username', 'password', 'email', 'mobile_number']


class SendResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def _get_user(self, email):
        user = get_object_or_none(User, email__iexact=email)
        return user

    def validate(self, attrs):
        super().validate(attrs)
        email = attrs.get("email")
        user = self._get_user(email)
        if not user:
            raise ValidationError({"detail": "Account with this email not found!"})

        attrs["user"] = user
        return attrs


class SendResetCodePhoneSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()

    def _get_user(self, mobile_number):
        user = get_object_or_none(User, mobile_number__iexact=mobile_number)
        return user

    def validate(self, attrs):
        super().validate(attrs)
        mobile_number = attrs.get("mobile_number")
        user = self._get_user(mobile_number)
        if not user:
            raise ValidationError({"detail": "Account with this mobile number not found!"})
        attrs["user"] = user
        return attrs


class ResetPasswordCodeSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    code = serializers.IntegerField()

    def _get_user(self, code):
        obj = get_object_or_none(PasswordResetConfirmation, code=code)
        if obj:
            return obj.user
        raise ValidationError("Code is incorrect")

    def _is_code_valid(self, code, user):
        confirmation = get_object_or_none(PasswordResetConfirmation, user=user)

        # Check if the code is matched with the password reset confirmation code
        if confirmation.code != code:
            return False
        else:
            # Check if the confirmation has been expired
            # The confirmation code should be active for the configured minute
            confirmation_expire = confirmation.created_at + timedelta(
                minutes=PASS_REST_CONFIRM_EXPIRE_MINUTE
            )
            # The confirmation token expire time has passed
            if timezone.now() > confirmation_expire:
                confirmation.delete()
                raise ValidationError("Password Reset Confirmation Code has Expired")

            # All thing passed. So the code is correct.
            return True

    def _check_password(self, new_pass, confirm_pass, user):
        # New password must match with the old password

        if confirm_pass != new_pass:
            msg = ("The two passwords do not match!")
            raise ValidationError(msg)

    def validate(self, attrs):
        super().validate(attrs)

        code = attrs.get("code")
        new_pass = attrs.get("password")
        confirm_pass = attrs.get("confirm_password")

        user = self._get_user(code)
        valid_code = self._is_code_valid(code=attrs["code"], user=user)
        if not valid_code:
            raise ValidationError("Code is incorrect")

        attrs["user"] = user

        self._check_password(new_pass=new_pass, confirm_pass=confirm_pass, user=user)

        errors = dict()
        try:
            # validate the password and catch the exception
            password_validation.validate_password(password=new_pass, user=user)
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def _validate_email(self, email, password):
        user = get_object_or_none(User, email__exact=email)
        if user and user.check_password(password):
            return user
        else:
            msg = 'Unable to log in with provided credentials.'
            raise ValidationError(msg, code=400)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:  # and company_id
            user = self._validate_email(email, password)
        else:
            msg = 'Must include "email" and "password".'
            raise ValidationError(msg, code=400)

        if not user or not user.auth_provider == 'credentials' or not user.is_visitor:
            msg = "Unable to log in with provided credentials."
            raise ValidationError(msg, code=400)

        attrs["user"] = user
        return attrs


class MobileNumberLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def _validate_number(self, mobile_number, password):
        user = get_object_or_none(User, mobile_number__exact=mobile_number)
        if user and user.check_password(password):
            return user
        else:
            msg = 'Unable to log in with provided credentials.'
            raise ValidationError(msg, code=400)

    def validate(self, attrs):
        mobile_number = attrs.get("mobile_number")
        password = attrs.get("password")

        if mobile_number and password:
            user = self._validate_number(mobile_number, password)
        else:
            msg = 'Must include "mobile number" and "password".'
            raise ValidationError(msg, code=400)

        if not user or not user.auth_provider == 'credentials' or not user.is_visitor:
            msg = "Unable to log in with provided credentials."
            raise ValidationError(msg, code=400)

        attrs["user"] = user
        return attrs


class OwnerEmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def _validate_email(self, email):
        user = get_object_or_none(User, email__exact=email)
        if user and (user.is_cafe_owner or user.is_cafe_manager):
            return user
        else:
            msg = 'Restaurant owner account not found with this email!'
            raise ValidationError(msg, code=400)

    def validate(self, attrs):
        email = attrs.get("email")

        if email:  # and company_id
            user = self._validate_email(email)
        else:
            msg = 'Must include "email" .'
            raise ValidationError(msg, code=400)

        if not user:
            msg = 'Restaurant owner account not found!'
            raise ValidationError(msg, code=400)

        if not user.is_cafe_owner and not user.is_cafe_manager:
            msg = 'Restaurant owner account not found!'
            raise ValidationError(msg, code=400)

        attrs["user"] = user
        return attrs


class OwnerMobileNumberLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True)

    # password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def _validate_number(self, mobile_number):
        user = get_object_or_none(User, mobile_number__exact=mobile_number)
        if user and (user.is_cafe_owner or user.is_cafe_manager):
            return user
        else:
            msg = 'Restaurant owner account not found with this mobile number!'
            raise ValidationError(msg, code=400)

    def validate(self, attrs):
        mobile_number = attrs.get("mobile_number")

        if mobile_number:
            user = self._validate_number(mobile_number)
        else:
            msg = 'Must include "mobile number" .'
            raise ValidationError(msg, code=400)

        if not user:
            msg = 'Restaurant owner account not found!'
            raise ValidationError(msg, code=400)

        if not user.is_cafe_owner and not user.is_cafe_manager:
            msg = 'Restaurant owner account not found!'
            raise ValidationError(msg, code=400)

        attrs["user"] = user
        return attrs


class OTPVerificationSerializer(serializers.Serializer):
    code = serializers.IntegerField()

    def _get_user(self, code):
        obj = get_object_or_none(TwoFactorVerificationOTP, code=code)
        if obj:
            return obj.user
        raise ValidationError("Code is incorrect")

    def _is_code_valid(self, code, user):
        confirmation = get_object_or_none(TwoFactorVerificationOTP, code=code, user=user)
        if not confirmation:
            raise ValidationError("Invalid otp!")
        else:
            # Check if the code is matched confirmation code
            if confirmation.code != code:
                return False
            else:
                # Check if the confirmation has been expired
                # The confirmation code should be active for the configured minute
                confirmation_expire = confirmation.created_at + timedelta(
                    minutes=VERIFICATION_CODE_EXPIRE_MINUTE
                )
                # The confirmation token expire time has passed
                if timezone.now() > confirmation_expire:
                    confirmation.delete()
                    raise ValidationError("Account verification code has Expired!")

                # All thing passed. So the code is correct.
                return True

    def validate(self, attrs):
        super().validate(attrs)
        code = attrs.get("code")
        user = self._get_user(code)
        valid_code = self._is_code_valid(code=attrs["code"], user=user)
        if not valid_code:
            raise ValidationError("Code is incorrect")
        attrs["user"] = user
        # errors = dict()
        # if errors:
        #     raise ValidationError(errors)

        return attrs


class OwnerRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)
    # password = serializers.CharField(style={"input_type": "password"}, write_only=True, required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'auth_provider', 'username', 'email', 'mobile_number', 'is_superuser', 'is_cafe_owner', 'is_cafe_manager', 'is_visitor', 'first_name', 'last_name', 'profile_image',
                  'date_of_birth',]
        read_only_fields = [
            'id', 'auth_provider', 'username', 'email', 'mobile_number', 'is_superuser', 'is_cafe_owner', 'is_cafe_manager', 'is_visitor'
        ]
