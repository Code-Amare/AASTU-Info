from django.db import connection
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.permissions import BasePermission


class JWTCookieAuthentication(JWTAuthentication):

    cookie_name = "access_token"

    def authenticate(self, request):

        access_token = request.COOKIES.get(self.cookie_name)

        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)

            if validated_token.get("tenant_schema") != connection.schema_name:
                raise AuthenticationFailed("This token is not valid for this tenant.")

            user = self.get_user(validated_token)

        except (InvalidToken, TokenError):
            raise AuthenticationFailed("Invalid or expired token.")

        self.enforce_csrf(request)

        return user, validated_token

    def enforce_csrf(self, request):
        SessionAuthentication().enforce_csrf(request)


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff is False
            and request.user.is_superuser is False
        )
