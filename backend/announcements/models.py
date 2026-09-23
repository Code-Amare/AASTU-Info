from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Announcement(models.Model):

    class Type(models.TextChoices):
        GENERAL = "GENERAL", "General"
        EXAM = "EXAM", "Exam"
        SUMMON = "SUMMON", "Summon"
        ASSIGNMENT = "ASSIGNMENT", "Assignment"

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="announcements"
    )

    target_audience = models.JSONField(
        help_text="List of target sections, e.g., ['section_3', 'section_4']"
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.GENERAL
    )

    is_active = models.BooleanField(default=True)
    allow_discussion = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
