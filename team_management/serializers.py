from rest_framework import serializers

from .models import Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description', 'editors']

    def create(self, validated_data):
        # Automatically set the owner to the current user
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)