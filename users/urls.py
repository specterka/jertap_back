from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import GoogleSocialAuthView, FacebookSocialAuthView, LoginWithEmailApi, LoginWithMobileNumberApi, RegistrationAPI, SendResetPasswordCode, ResetPassword, OwnerLoginWithEmailApi, \
    OwnerLoginWithMobileNumberApi, VerifyLoginOTP, OwnerRegistrationApi, SendResetPasswordCodeOnNumber, UserDetailsView

app_name = 'users'
users_api_v1_urlpatterns = [
    path('token-refresh/', TokenRefreshView.as_view(), name='refresh jwt auth token using refresh token'),
    path("login-with/google/", GoogleSocialAuthView.as_view(), name='Google Login'),
    # path("login-with/fb/", FacebookSocialAuthView.as_view(), name='Fb Login'),
    path("login-with/email/", LoginWithEmailApi.as_view(), name='Email Login'),
    path("login-with/mobile-number/", LoginWithMobileNumberApi.as_view(), name='Mobile number Login'),

    path('registration/', RegistrationAPI.as_view(), name='User registration'),

    path('send-password-reset-code-mail/', SendResetPasswordCode.as_view(), name='Send Password Reset Code in mail'),
    path('send-password-reset-code-mobile/', SendResetPasswordCodeOnNumber.as_view(), name='Send Password Reset Code in sms'),
    path('reset-password/', ResetPassword.as_view(), name='Password reset using code'),

    path('owner-login-with/email/', OwnerLoginWithEmailApi.as_view(), name='Owner Login With Email'),
    path('owner-login-with/mobile-number/', OwnerLoginWithMobileNumberApi.as_view(), name='Owner Login With mobile number'),
    path('owner-login/verify-login-otp/', VerifyLoginOTP.as_view(), name='Verify login otp '),
    path('owner-registration/', OwnerRegistrationApi.as_view(), name='Owner registration '),

    path('user-profile/', UserDetailsView.as_view(), name='User profile'),

]
