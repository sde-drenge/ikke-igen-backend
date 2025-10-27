from rest_framework import serializers

from .models import Workplace


class WorkplaceSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Workplace
        fields = [
            "uuid",
            "name",
            "vat",
            "website",
            "createdAt",
            "updatedAt",
        ]


class LightWorkplaceSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")

    class Meta:
        model = Workplace
        fields = [
            "uuid",
            "name",
            "website",
        ]
