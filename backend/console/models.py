from django.db import models
from cloudinary.models import CloudinaryField


class PlatformSettings(models.Model):

    # Branding / identity
    site_name = models.CharField(max_length=100, default="MegaLearn")
    logo = CloudinaryField("logo", blank=True, null=True)
    support_email = models.EmailField(blank=True, default="")
    support_phone = models.CharField(max_length=32, blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Platform Settings"
