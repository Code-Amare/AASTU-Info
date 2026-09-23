from rest_framework import serializers
from .models import PlatformSettings


class PlatformSettingsSerializer(serializers.ModelSerializer):
    site_logo = serializers.SerializerMethodField()

    class Meta:
        model = PlatformSettings
        fields = [
            "site_name",
            "site_logo",
            "support_email",
            "support_phone",
            "updated_at",
        ]
        read_only_fields = fields

    def get_site_logo(self, instance) -> str | None:
        if not instance.logo:
            return None

        # 1. Primary: Use Cloudinary's native secure URL generator
        if hasattr(instance.logo, "build_url"):
            return instance.logo.build_url(secure=True)

        # 2. Fallback string URL processing
        url = instance.logo.url if hasattr(instance.logo, "url") else str(instance.logo)

        if url.startswith("http://"):
            return "https://" + url[7:]
        if not url.startswith("https://"):
            return f'https://{url.lstrip("/")}'

        return url
