from rest_framework import serializers
from .models import UserUpload

class UserUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUpload
        fields = [
            'id',
            'upload_type',
            'file',
            'description',
            'created_at',
            'published_at',
            'status',
            'tags',
        ]
        read_only_fields = ['id', 'created_at', 'published_at', 'status']

    def validate_file(self, value):
        """
        Validate the file extension.
        """
        UserUpload.validate_file_extension(value)
        return value