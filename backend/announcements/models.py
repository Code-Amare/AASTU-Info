from django.db import models
from cloudinary.models import CloudinaryField
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

    target_audience = models.ManyToManyField(
        User,
        related_name="targeted_announcements",
        blank=True,
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


class Event(models.Model):
    announcement = models.OneToOneField(
        Announcement, on_delete=models.CASCADE, related_name="event_details"
    )

    event_date = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"Event for: {self.announcement.title}"


class Attachment(models.Model):
    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name="attachments"
    )

    file = CloudinaryField(
        "aastu-info/attachments", resource_type="auto", blank=True, null=True
    )
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=50, help_text="e.g., application/pdf, image/jpeg"
    )
    file_size_mb = models.FloatField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.announcement.title})"


class Discussion(models.Model):
    class MessageType(models.TextChoices):
        TEXT = "TEXT", "Text"
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"
        VOICE = "VOICE", "Voice Note"
        FILE = "FILE", "Document"

    announcement = models.ForeignKey(
        "Announcement", on_delete=models.CASCADE, related_name="discussions"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="discussion_messages",
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    message_type = models.CharField(
        max_length=10, choices=MessageType.choices, default=MessageType.TEXT
    )

    text = models.TextField(blank=True, null=True)

    media_file = CloudinaryField(
        "aastu-info/discussions", resource_type="auto", blank=True, null=True
    )

    media_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.message_type}] {self.sender.username} on Announcement #{self.announcement.id}"
