from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import PlatformSettings
from .serializer import PlatformSettingsSerializer


class PlatformSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            settings = PlatformSettings.get_solo()
        except PlatformSettings.DoesNotExist:
            return Response(
                {"error": "Platform settings not set yet"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlatformSettingsSerializer(settings).data

        return Response(serializer, status=status.HTTP_200_OK)
