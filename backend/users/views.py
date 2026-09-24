from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db import transaction
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from axes.utils import reset
from axes.handlers.proxy import AxesProxyHandler

from .serializers import (
    UserSerializer,
    RequestPasswordResetSerializer,
    ResetPasswordConfirmSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    SendVerificationCodeSerializer,
    EmailLoginRequestSerializer,
    EmailVerifyViewSerializer,
)
from .models import EmailOTP, EmailLoginLink, ResetPasswordLink
from utils.emails import (
    send_verification_code_email,
    send_login_link_email,
    send_login_alert_email,
    send_password_reset_link_email,
)

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def generate_tokens_for_user(request, user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    response = Response(
        {
            "access_length": access_token,
            "refresh_length": refresh_token,
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )

    return response


class MeView(APIView):
    def get(self, request):
        user = request.user
        return Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Log in",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Logged in, or a verification/2FA step is required.",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"access_length": 220, "refresh_length": 240, "user": {}},
                    ),
                    OpenApiExample(
                        "Verification required",
                        value={
                            "error": "You are not Verified yet.",
                            "verification_required": True,
                            "email": "user@example.com",
                        },
                    ),
                    OpenApiExample(
                        "2FA link sent",
                        value={
                            "detail": "A login link has been sent to your email address.",
                            "twofa_required": True,
                        },
                    ),
                ],
            ),
            401: OpenApiResponse(description="Invalid credentials."),
            403: OpenApiResponse(
                description="Account locked due to too many failed attempts."
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username_or_email = serializer.validated_data["username_or_email"]
        password = serializer.validated_data["password"]

        if not username_or_email or not password:
            return Response(
                {"error": "Username/Email and Password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=username_or_email).first()
        if not user:
            user = User.objects.filter(email=username_or_email).first()

        if not user:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )

        username = user.username

        if AxesProxyHandler.is_locked(request, credentials={"username": username}):
            return Response(
                {
                    "error": "Account locked: too many login attempts. Please try again later."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.two_factor_enabled:
            login_link = EmailLoginLink.objects.filter(user=user).first()

            if login_link and not login_link.is_expired():
                return Response(
                    {
                        "error": "Login link already sent, please try later to request a new one."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if login_link:
                login_link.delete()
            new_login_link = EmailLoginLink.objects.create(user=user)

            try:
                send_login_link_email(user=user, code=new_login_link.code)
            except Exception:
                new_login_link.delete()
                return Response(
                    {
                        "error": (
                            "Unable to send the login link. Please try again later."
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "detail": "A login link has been sent to your email address.",
                    "twofa_required": True,
                },
                status=status.HTTP_200_OK,
            )

        try:
            send_login_alert_email(user, request)
        except Exception:
            logger.exception("Failed to send login alert email for user %s", user.pk)

        return generate_tokens_for_user(request, user)


class EmailLoginRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Email Login Link Request",
        request=EmailLoginRequestSerializer,
        responses=None,
    )
    def post(self, request):
        email = request.data.get("email", "").strip()

        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )
        login_link = EmailLoginLink.objects.filter(user=user).first()

        if login_link and not login_link.is_expired():
            return Response(
                {
                    "error": "Login link already sent, please try later to request a new one."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if login_link:
            login_link.delete()
        new_login_link = EmailLoginLink.objects.create(user=user)

        try:
            send_login_link_email(user=user, code=new_login_link.code)
        except Exception:
            new_login_link.delete()
            return Response(
                {"error": ("Unable to send the login link. Please try again later.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "detail": "A login link has been sent to your email address.",
            },
            status=status.HTTP_200_OK,
        )


class LoginViaEmailView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, code):
        if not code:
            return Response(
                {"error": "Invalid login link."}, status=status.HTTP_400_BAD_REQUEST
            )

        login_link = EmailLoginLink.objects.filter(code=code).first()

        if not login_link or login_link.is_expired():
            return Response(
                {"error": "This login link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = login_link.user

        with transaction.atomic():
            user.email_verified = True
            user.save(update_fields=["email_verified"])
            reset(username=user.email)
            login_link.delete()

        return generate_tokens_for_user(request, user)


class SendVerificationCodeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Send Verification Code",
        request=SendVerificationCodeSerializer,
        responses=None,
    )
    def post(self, request):
        email = request.data.get("email", "").strip()

        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "Invalid Email."}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.email_verified:
            return Response(
                {"error": "Email already verified."}, status=status.HTTP_400_BAD_REQUEST
            )

        email_verify = EmailOTP.objects.filter(
            user=user, purpose=EmailOTP.Purpose.EMAIL_VERIFICATION
        ).first()

        if email_verify and not email_verify.is_expired():
            return Response(
                {"error": "Verification email already sent. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if email_verify:
                email_verify.delete()

            email_otp = EmailOTP.objects.create(
                user=user, purpose=EmailOTP.Purpose.EMAIL_VERIFICATION
            )

        try:
            send_verification_code_email(user=user, code=email_otp.code)
        except Exception:
            email_otp.delete()
            return Response(
                {"detail": "Unable to send the verification code."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"detail": "Verification code sent successfully."},
            status=status.HTTP_200_OK,
        )


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    MAX_ATTEMPTS = 5

    @extend_schema(
        summary="Email Verify View",
        request=EmailVerifyViewSerializer,
        responses=None,
    )
    def post(self, request):
        serializer = EmailVerifyViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        if not email or not code:
            return Response(
                {"error": "Email and verification code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "Invalid email or code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            otp = EmailOTP.objects.get(
                user=user, purpose=EmailOTP.Purpose.EMAIL_VERIFICATION
            )
        except EmailOTP.DoesNotExist:
            return Response(
                {"error": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.is_expired():
            otp.delete()
            return Response(
                {"error": "Verification code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.attempts >= self.MAX_ATTEMPTS:
            otp.delete()
            return Response(
                {
                    "error": (
                        "Too many failed attempts. Please request a new verification code."
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if not otp.verify(code):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])

            remaining_attempts = self.MAX_ATTEMPTS - otp.attempts

            if remaining_attempts <= 0:
                otp.delete()
                return Response(
                    {
                        "error": (
                            "Too many failed attempts. Please request a new verification code."
                        )
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            return Response(
                {
                    "error": "Invalid verification code.",
                    "remaining_attempts": remaining_attempts,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user.email_verified = True
            user.save(update_fields=["email_verified"])
            otp.delete()

        return generate_tokens_for_user(request, user)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Request a password reset code",
        request=RequestPasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                description="If an account exists for this email, a reset code has been sent.",
                examples=[
                    OpenApiExample(
                        "Sent",
                        value={
                            "detail": "If an account exists for this email, a reset code has been sent."
                        },
                    )
                ],
            ),
        },
    )
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()

        generic_response = Response(
            {
                "detail": "If an account exists for this email, a reset code has been sent."
            },
            status=status.HTTP_200_OK,
        )

        if not user:
            return generic_response

        existing = ResetPasswordLink.objects.filter(user=user).first()

        if existing and not existing.is_expired():
            return generic_response

        with transaction.atomic():
            if existing:
                existing.delete()

            link = ResetPasswordLink.objects.create(user=user)

        try:
            send_password_reset_link_email(user=user, code=link.code)
        except Exception:
            link.delete()
            logger.exception("Failed to send password reset email for user %s", user.pk)
        return generic_response


class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Confirm a password reset with the emailed code",
        request=ResetPasswordConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successfully."),
            400: OpenApiResponse(description="Invalid, expired, or already-used code."),
        },
    )
    def post(self, request, code):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]

        link = ResetPasswordLink.objects.filter(code=code).first()

        if not link:
            return Response(
                {"error": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = link.user

        if user.check_password(new_password):
            return Response(
                {
                    "error": "Your new password must be different from your current password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if link.is_expired():
            link.delete()
            return Response(
                {"error": "Verification code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user.set_password(new_password)
            user.save(update_fields=["password"])
            reset(username=user.email)
            link.delete()

        return Response(
            {"detail": "Password reset successfully."}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):

    @extend_schema(
        summary="Change password while logged in",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully."),
            400: OpenApiResponse(
                description="Current password is incorrect, or new password fails validation."
            ),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]

        user = request.user
        if user.check_password(new_password):
            return Response(
                {
                    "error": "Your new password must be different from your current password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )
