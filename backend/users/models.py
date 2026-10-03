import uuid
import random
import secrets
from datetime import timedelta
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        unique=True,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    profile_picture = CloudinaryField(
        "aastu-info/profile_picture",
        blank=True,
        null=True,
    )

    two_factor_enabled = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20)
    role = models.CharField(
        max_length=10,
        choices=ROLE,
        default="student",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    section = models.CharField(
        max_length=20,
        blank=True,
    )


class EmailOTP(models.Model):
    class Purpose(models.TextChoices):
        EMAIL_VERIFICATION = "email_verification", "Email verification"
        PASSWORD_RESET = "password_reset", "Password reset"
        SUBSCRIPTION_CANCELLATION = (
            "subscription_cancellation",
            "Subscription cancellation",
        )

    def generate_otp_code() -> str:
        return "".join(random.choices("0123456789", k=6))

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_otps",
    )
    purpose = models.CharField(
        max_length=32,
        choices=Purpose.choices,
        default=Purpose.EMAIL_VERIFICATION,
    )
    code = models.CharField(max_length=6, default=generate_otp_code)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    EXPIRY_MINUTES = 7

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "purpose"], name="unique_otp_per_user_purpose"
            )
        ]

    def __str__(self):
        return f"{self.get_purpose_display()} code for {self.user}"

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=self.EXPIRY_MINUTES)

    def verify(self, raw_code: str) -> bool:
        return secrets.compare_digest(str(raw_code), self.code)


class EmailLoginLink(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_codes",
    )
    code = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    EXPIRY_MINUTES = 10

    def __str__(self):
        return f"Login link for {self.user}"

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=self.EXPIRY_MINUTES)


class ResetPasswordLink(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reset_codes",
    )
    code = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    EXPIRY_MINUTES = 10

    def __str__(self):
        return f"Login link for {self.user}"

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=self.EXPIRY_MINUTES)
