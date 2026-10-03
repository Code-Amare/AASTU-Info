from django.contrib.auth import get_user_model
from rest_framework import serializers
from cloudinary.models import CloudinaryField
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "department",
            "section",
            "email_verified",
            "two_factor_enabled",
            "is_staff",
            "is_superuser",
        ]

        read_only_fields = [
            "id",
            "username",
            "email",
            "full_name",
            "email_verified",
            "is_staff",
            "is_superuser",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if "profile_picture" in validated_data:
            is_self = (
                request and request.user.is_authenticated and request.user == instance
            )

            is_privileged = (
                request
                and request.user.is_authenticated
                and (request.user.is_staff or request.user.is_superuser)
            )

            if not (is_self or is_privileged):
                raise serializers.ValidationError(
                    {
                        "profile_picture": (
                            "You do not have permission to update "
                            "the profile picture."
                        )
                    }
                )

        return super().update(instance, validated_data)


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailVerifyViewSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    def validate_code(self, value):
        value = value.strip()
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Invalid verification code.")
        return value


class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    def validate_old_password(self, value):
        request = self.context["request"]
        if not request.user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
