from rest_framework import serializers

from .models import School


class SchoolSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    createdAt = serializers.DateTimeField(read_only=True)

    class Meta:
        model = School
        fields = [
            "uuid",
            "name",
            "address",
            "createdAt",
        ]
