from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone

from .models import BaseUser, GoogleTokens

class InputSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    state = serializers.CharField(required=False)

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = "__all__"


class GoogleTokensUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleTokens
        fields = ['access_token', 'refresh_token']

    def update(self, instance, validated_data):
        # Update the access token and refresh token
        instance.access_token = validated_data.get('access_token', instance.access_token)
        instance.refresh_token = validated_data.get('refresh_token', instance.refresh_token)

        # Calculate and update the expiration time (e.g., 59 minutes from now)
        expiration_time = timezone.now() + timezone.timedelta(minutes=59)
        instance.expires_at = expiration_time

        instance.save()
        return instance