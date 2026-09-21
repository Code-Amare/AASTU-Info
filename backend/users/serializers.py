from django.contrib.auth import get_user_model
from rest_framework import serializers
from cloudinary.models import CloudinaryField
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "email_verified",
            "two_factor_enabled",
            "is_owner",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "full_name",
            "is_owner",
            "is_staff",
            "is_superuser",
        ]

    def update(self, instance, validated_data):
        request = self.context.get("request")
        old_picture = None

        if "profile_picture" in validated_data:
            is_self = (
                request and request.user.is_authenticated and request.user == instance
            )
            is_privileged = (
                request
                and request.user.is_authenticated
                and (
                    request.user.is_owner
                    or request.user.is_staff
                    or request.user.is_superuser
                )
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

            old_picture = instance.profile_picture or None
            # "profile_picture" stays in validated_data — super().update()
            # sets and saves it normally along with every other field.

        instance = super().update(instance, validated_data)

        if old_picture:
            old_picture.delete(save=False)  # instance already saved above

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
            "date_of_birth",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(
            is_owner=True,
            email_verified=False,
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user


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
