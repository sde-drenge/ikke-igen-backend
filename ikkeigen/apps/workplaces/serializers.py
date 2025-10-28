from django.core.cache import cache
from django.db.models import Avg
from rest_framework import serializers
from users.serializers import LightUserSerializer, UserSerializer

from .models import Review, Workplace


class WorkplaceSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)
    stars = serializers.SerializerMethodField()
    amountOfReviews = serializers.SerializerMethodField()

    class Meta:
        model = Workplace
        fields = [
            "uuid",
            "stars",
            "name",
            "vat",
            "website",
            "amountOfReviews",
            "createdAt",
            "updatedAt",
        ]

    def get_stars(self, obj: Workplace):
        cacheKey = f"workplace:{obj.pk}:AverageStars"
        cachedValue = cache.get(cacheKey)
        if cachedValue is not None:
            return cachedValue

        reviews = obj.reviews.filter(
            deletedAt__isnull=True, verifiedBy__isnull=False
        ).aggregate(averageStars=Avg("stars"))
        averageStars = reviews["averageStars"] or 0

        cache.set(cacheKey, averageStars, timeout=900)
        return averageStars

    def get_amountOfReviews(self, obj: Workplace):
        cacheKey = f"workplace:{obj.pk}:amountOfReviews"
        cachedValue = cache.get(cacheKey)
        if cachedValue is not None:
            return cachedValue

        amountOfReviews = obj.reviews.filter(
            deletedAt__isnull=True, verifiedBy__isnull=False
        ).count()
        cache.set(cacheKey, amountOfReviews, timeout=900)
        return amountOfReviews


class LightWorkplaceSerializer(WorkplaceSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")

    class Meta:
        model = Workplace
        fields = [
            "uuid",
            "stars",
            "name",
            "website",
            "amountOfReviews",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)
    author = UserSerializer(read_only=True)
    workplace = LightWorkplaceSerializer(read_only=True)
    verifiedBy = LightUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "uuid",
            "stars",
            "title",
            "comment",
            "author",
            "workplace",
            "verifiedBy",
            "createdAt",
            "updatedAt",
        ]
