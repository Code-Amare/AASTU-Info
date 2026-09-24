from django.urls import path

from .views import (
    LoginView,
    LoginViaEmailView,
    SendVerificationCodeView,
    EmailVerifyView,
    RequestPasswordResetView,
    ResetPasswordConfirmView,
    ChangePasswordView,
    EmailLoginRequestView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("login/email/request/", EmailLoginRequestView.as_view()),
    path("login/email/<uuid:code>/", LoginViaEmailView.as_view()),
    path("email/verify/request/", SendVerificationCodeView.as_view()),
    path("email/verify/", EmailVerifyView.as_view()),
    path("password/reset/request/", RequestPasswordResetView.as_view()),
    path("password/reset/<uuid:code>/", ResetPasswordConfirmView.as_view()),
    path("password/change/", ChangePasswordView.as_view()),
]
