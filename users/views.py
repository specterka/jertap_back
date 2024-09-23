from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.throttling import AnonRateThrottle
from core.models import Restaurant
from jertap_backend.settings import SOCIAL_SECRET
from users.email_and_sms import send_email, send_message
from users.models import User, PasswordResetConfirmation, TwoFactorVerificationOTP
from users.serializers import GoogleSocialAuthSerializer, FacebookSocialAuthSerializer, ManualRegistrationSerializer, generate_username, SendResetCodeSerializer, ResetPasswordCodeSerializer, \
    EmailLoginSerializer, MobileNumberLoginSerializer, OTPVerificationSerializer, OwnerEmailLoginSerializer, OwnerMobileNumberLoginSerializer, OwnerRegistrationSerializer, \
    SendResetCodePhoneSerializer, UserProfileSerializer


# Create your views here.

class GoogleSocialAuthView(GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])

        return Response(data, status=status.HTTP_200_OK)


class FacebookSocialAuthView(GenericAPIView):
    serializer_class = FacebookSocialAuthSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)


class RegistrationAPI(GenericAPIView):
    serializer_class = ManualRegistrationSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        mobile_number = serializer.validated_data["mobile_number"]

        users_with_email = User.objects.filter(email__iexact=email)
        if users_with_email.exists():
            return Response({"details": "User already exist with this email"}, status=status.HTTP_400_BAD_REQUEST)
        users_with_mobile = User.objects.filter(mobile_number__iexact=mobile_number)
        if users_with_mobile.exists():
            return Response({"details": "User already exist with this mobile number"}, status=status.HTTP_400_BAD_REQUEST)

        user = User(email=email, username=generate_username(username), mobile_number=mobile_number, is_visitor=True)
        user.set_password(password)
        user.save()
        return Response(data={"data": serializer.data, 'tokens': user.tokens(), "details": "User created successfully!"}, status=status.HTTP_200_OK)


class SendResetPasswordCode(GenericAPIView):
    serializer_class = SendResetCodeSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        try:
            user.pass_reset_confirmation.delete()
        except Exception as e:
            pass
        if user:
            otp_obj = PasswordResetConfirmation.objects.generate(user=user)
            # send an email with verification code
            send_email('Password Reset Code', f'<p><strong style="color: #336699;">{otp_obj.code}</strong> is your password reset code, It will valid for only 5 minutes</p>', [user.email, ])

            return Response({'details': 'otp sent successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'details': 'User not found!'}, status=status.HTTP_400_BAD_REQUEST)


class SendResetPasswordCodeOnNumber(GenericAPIView):
    serializer_class = SendResetCodePhoneSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        try:
            user.pass_reset_confirmation.delete()
        except Exception as e:
            pass
        if user:
            otp_obj = PasswordResetConfirmation.objects.generate(user=user)
            # send a sms with verification code

            return Response({'details': 'otp sent successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'details': 'User not found!'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(CreateAPIView):
    serializer_class = ResetPasswordCodeSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        if user:
            password = serializer.validated_data['password']
            with transaction.atomic():
                user.set_password(password)
                user.save(update_fields=('password',))
                user.pass_reset_confirmation.delete()
        return Response({"detail": "Password reset successfully"}, status=status.HTTP_201_CREATED)


class LoginWithEmailApi(GenericAPIView):
    serializer_class = EmailLoginSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user_data = UserProfileSerializer(instance=user).data
        return Response({
            'tokens': user.tokens(),
            'user': user_data,
        }, status=status.HTTP_200_OK)


class LoginWithMobileNumberApi(LoginWithEmailApi):
    serializer_class = MobileNumberLoginSerializer


class OwnerLoginWithEmailApi(GenericAPIView):
    serializer_class = OwnerEmailLoginSerializer
    permission_classes = [AllowAny, ]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        try:
            user.two_factor_otp.delete()
        except Exception as e:
            pass
        if user:
            otp_obj = TwoFactorVerificationOTP.objects.generate(user=user)
            # send an email with verification code
            send_email('Login Verification Code', f'<p><strong style="color: #336699;">{otp_obj.code}</strong> is your login verification code, It will valid for only 5 minutes</p>', [user.email, ])
            return Response({'details': 'otp sent successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'details': 'User not found!'}, status=status.HTTP_200_OK)


class OwnerLoginWithMobileNumberApi(GenericAPIView):
    serializer_class = OwnerMobileNumberLoginSerializer
    permission_classes = [AllowAny, ]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        try:
            user.two_factor_otp.delete()
        except Exception as e:
            pass
        if user:
            otp_obj = TwoFactorVerificationOTP.objects.generate(user=user)
            # send sms with verification code
            send_message(phones=user.mobile_number, message=f'{otp_obj.code} is your login verification otp, It will valid for five minutes')

            return Response({'details': 'otp sent successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'details': 'User not found!'}, status=status.HTTP_200_OK)


class VerifyLoginOTP(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        user_data = UserProfileSerializer(instance=user).data
        try:
            user.two_factor_otp.all().delete()

        except:
            pass

        return Response({
            'tokens': user.tokens(),
            'user': user_data,
        }, status=status.HTTP_200_OK)


class OwnerRegistrationApi(GenericAPIView):
    serializer_class = OwnerRegistrationSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        # password = serializer.validated_data["password"]
        username = serializer.validated_data["username"]
        mobile_number = serializer.validated_data["mobile_number"]

        # users = User.objects.filter(email__iexact=email)
        # if users.count() > 0:
        #     if users[0].is_cafe_owner or users[0].is_cafe_manager:
        #         return Response({"details": "User already exist with this email"}, status=status.HTTP_400_BAD_REQUEST)
        #     else:
        #         users[0].is_cafe_owner = True
        #         users[0].save()
        #         try:
        #             users[0].two_factor_otp.delete()
        #         except Exception as e:
        #             pass
        #         otp_obj = TwoFactorVerificationOTP.objects.generate(user=users[0])
        #         # send an email with verification code
        #         send_email('Login Verification Code', f'<p><strong style="color: #336699;">{otp_obj.code}</strong> is your login verification code, It will valid for only 5 minutes</p>',
        #                    [users[0].email, ])
        #
        #         # send sms with verification code
        #         send_message(phones=users[0].mobile_number, message=f'{otp_obj.code} is your login verification otp, It will valid for five minutes')
        #
        #         return Response(data={"details": "User created successfully!", }, status=status.HTTP_200_OK)
        #
        # users = User.objects.filter(mobile_number__iexact=mobile_number)
        # if users.count() > 0:
        #     if users[0].is_cafe_owner or users[0].is_cafe_manager:
        #         return Response({"details": "User already exist with this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
        #     else:
        #         users[0].is_cafe_owner = True
        #         users[0].save()
        #         try:
        #             users[0].two_factor_otp.delete()
        #         except Exception as e:
        #             pass
        #         otp_obj = TwoFactorVerificationOTP.objects.generate(user=users[0])
        #         # send an email with verification code
        #         send_email('Login Verification Code', f'<p><strong style="color: #336699;">{otp_obj.code}</strong> is your login verification code, It will valid for only 5 minutes</p>',
        #                    [users[0].email, ])
        #         # send sms with verification code
        #         send_message(phones=users[0].mobile_number, message=f'{otp_obj.code} is your login verification otp, It will valid for five minutes')
        #
        #         return Response(data={"details": "User created successfully!", }, status=status.HTTP_200_OK)

        users_with_email = User.objects.filter(email__iexact=email)
        if users_with_email.exists():
            return Response({"details": "User already exist with this email"}, status=status.HTTP_400_BAD_REQUEST)
        users_with_mobile = User.objects.filter(mobile_number__iexact=mobile_number)
        if users_with_mobile.exists():
            return Response({"details": "User already exist with this mobile number"}, status=status.HTTP_400_BAD_REQUEST)

        user = User(email=email, username=generate_username(username), mobile_number=mobile_number, is_cafe_owner=True, password=SOCIAL_SECRET)
        user.save()
        # create Verification otp
        try:
            user.two_factor_otp.delete()
        except Exception as e:
            pass
        otp_obj = TwoFactorVerificationOTP.objects.generate(user=user)
        # send an email with verification code
        send_email('Login Verification Code', f'<p><strong style="color: #336699;">{otp_obj.code}</strong> is your login verification code, It will valid for only 5 minutes</p>', [user.email, ])
        # send sms with verification code
        send_message(phones=user.mobile_number, message=f'{otp_obj.code} is your login verification otp, It will valid for five minutes')

        return Response(data={"details": "User created successfully!", }, status=status.HTTP_200_OK)


class UserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'user': serializer.data, }, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def patch(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}
    #     return Response({'details': 'Details updated successfully'}, status=status.HTTP_200_OK)
