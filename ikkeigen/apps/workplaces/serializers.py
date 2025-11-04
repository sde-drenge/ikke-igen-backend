from django.core.cache import cache
from django.db.models import Avg
from rest_framework import serializers
from users.serializers import LightUserSerializer, UserSerializer

from .models import Category, Review, TopCategory, Workplace


class CategorySerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    topCategory = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "name",
            "uuid",
            "topCategory",
        ]

    def get_topCategory(self, obj: Category):
        topCategory = obj.top_categories.first()
        if topCategory:
            return LightTopCategorySerializer(topCategory).data
        return None


class LightCategorySerializer(CategorySerializer):
    class Meta:
        model = Category
        fields = [
            "name",
            "uuid",
        ]


class TopCategorySerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    categories = LightCategorySerializer(many=True, read_only=True)

    class Meta:
        model = TopCategory
        fields = [
            "name",
            "categories",
            "color",
            "uuid",
        ]


class LightTopCategorySerializer(TopCategorySerializer):
    class Meta:
        model = TopCategory
        fields = [
            "name",
            "color",
            "uuid",
        ]


class WorkplaceSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)
    stars = serializers.SerializerMethodField()
    amountOfReviews = serializers.SerializerMethodField()
    starsProcentages = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Workplace
        fields = [
            "uuid",
            "stars",
            "name",
            "vat",
            "address",
            "amountOfReviews",
            "starsProcentages",
            "categories",
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

        # Rounding up
        averageStars = str(round(averageStars * 2) / 2)
        cache.set(cacheKey, averageStars, timeout=900)
        return averageStars

    def get_starsProcentages(self, obj: Workplace):
        cacheKey = f"workplace:{obj.pk}:starsProcentages"
        cachedValue = cache.get(cacheKey)
        if cachedValue is not None:
            return cachedValue

        data = {}
        totalReviews = obj.reviews.filter(
            deletedAt__isnull=True, verifiedBy__isnull=False
        ).count()

        starOptions = [
            "1",
            "2",
            "3",
            "4",
            "5",
        ]
        for starOption in starOptions:
            if totalReviews == 0:
                data[starOption] = "0"
                continue

            count = obj.reviews.filter(
                deletedAt__isnull=True, verifiedBy__isnull=False, stars=starOption
            ).count()
            data[starOption] = str(round((count / totalReviews) * 100))
        cache.set(cacheKey, data, timeout=60 * 15)  # Cache for 15 minutes
        return data

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
            "address",
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
