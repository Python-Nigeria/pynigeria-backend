from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    # Displaying username 
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        # fields = [
        #     'id', 'user', 'bio', 'skills', 'github', 
        #     'portfolio', 'location', 'experience_level', 
        #     'avatar', 'username', 'created_at'
        # ]
        fields = "__all__"
        read_only_fields = ['id', 'user', 'created_at']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'bio', 'skills', 'github', 'portfolio', 
            'location', 'experience_level', 'username'
        ]


class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar']