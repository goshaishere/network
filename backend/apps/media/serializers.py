from rest_framework import serializers

from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ("id", "file", "created_at")
        read_only_fields = ("id", "created_at")
