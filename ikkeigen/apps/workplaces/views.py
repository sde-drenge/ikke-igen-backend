from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from schools.models import School
from settings.middleware.error_handling import CustomAPIView
from users.models import User
from users.views import BasicPageination

from .models import Category, Review, TopCategory, Workplace
from .serializers import (
    CategorySerializer,
    LightWorkplaceSerializer,
    ReviewSerializer,
    TopCategorySerializer,
    WorkplaceSerializer,
)
from .utils import createWorkplaceByVATNumber


class SearchWorkPlacesView(CustomAPIView, BasicPageination):
    """
    <GET> returns paginatied list of workplaces
    ?search=<str>
    ?categoryUuid=<uuid>
    """

    serializer_class = LightWorkplaceSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "")

        filter = (
            Q(name__icontains=search, deletedAt__isnull=True)
            | Q(vat__icontains=search, deletedAt__isnull=True)
            | Q(address__icontains=search, deletedAt__isnull=True)
        )

        categoryUuid = request.GET.get("categoryUuid", None)
        if categoryUuid:
            filter &= Q(categories__uuid=categoryUuid, deletedAt__isnull=True)

        workplaces = Workplace.objects.filter(filter)

        if not workplaces.exists():
            createdNew = createWorkplaceByVATNumber(search)
            if createdNew:
                workplaces = Workplace.objects.filter(
                    Q(name__icontains=search, deletedAt__isnull=True)
                    | Q(vat__icontains=search, deletedAt__isnull=True)
                    | Q(address__icontains=search, deletedAt__isnull=True)
                )

        paginated = self.paginate(workplaces, request)
        return Response(data=paginated.data, status=status.HTTP_200_OK)


class CreateWorkPlaceView(CustomAPIView):
    """
    <POST> creates a new workplace
    """

    serializer_class = WorkplaceSerializer
    # authentication_classes = []
    # permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class GetWorkplaceView(CustomAPIView):
    """
    <GET> returns a workplace by uuid
    """

    serializer_class = WorkplaceSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        workplace_id = kwargs.get("workplaceUuid")
        workplace = Workplace.objects.get(uuid=workplace_id, deletedAt__isnull=True)
        serializer = self.serializer_class(workplace)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RequestWorkplaceReviewView(CustomAPIView):
    """
    <POST> request a review for a workplace
    Data: {
        "comment": "string",
        "stars": Decimal,
        "titel": "string",
    }
    """

    serializer_class = ReviewSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        workplaceUuid = kwargs.get("workplaceUuid")
        workplace = get_object_or_404(
            Workplace, uuid=workplaceUuid, deletedAt__isnull=True
        )

        stars = data.get("stars")
        stars = float(stars)
        if stars > 5 or stars < 0:
            return Response(
                data={"detail": "Stjerner skal være mellem 0 og 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, workplace=workplace)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyWorkplaceReviewView(CustomAPIView):
    """
    <POST> verify a workplace review
    Data: {
        "reviewUuid": "string",
    }
    """

    roleNeeded = ["teacher", "teacher-admin"]

    def post(self, request, *args, **kwargs):
        review_uuid = kwargs.get("reviewUuid")
        review: Review = get_object_or_404(
            Review, uuid=review_uuid, deletedAt__isnull=True
        )

        author: User = review.author
        school = author.schools.first()
        if (
            not school
            or not school.teachers.filter(
                uuid=request.user.uuid, deletedAt__isnull=True
            ).exists()
        ):
            return Response(
                data={
                    "detail": "Du har ikke tilladelse til at verificere denne anmeldelse."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        review.verifiedBy = request.user
        review.save()
        serializer = ReviewSerializer(review)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GetUnverifiedReviewsView(CustomAPIView, BasicPageination):
    """
    <GET> returns a list of unverified reviews
    """

    roleNeeded = ["teacher", "teacher-admin"]
    serializer_class = ReviewSerializer

    def get(self, request, *args, **kwargs):
        school: School = request.user.teachingSchools.first()
        if not school:
            return Response(
                data={"detail": "Du har ikke tilladelse til at se anmeldelser."},
                status=status.HTTP_403_FORBIDDEN,
            )
        reviews = Review.objects.filter(
            verifiedBy__isnull=True, deletedAt__isnull=True, author__schools=school
        ).order_by("createdAt")

        data = self.paginate(reviews, request).data
        return Response(data=data, status=status.HTTP_200_OK)


class DeclineWorkplaceReviewView(CustomAPIView):
    """
    <POST> decline a workplace review
    """

    roleNeeded = ["teacher", "teacher-admin"]

    def delete(self, request, *args, **kwargs):
        reviewUuid = kwargs.get("reviewUuid")
        review: Review = get_object_or_404(
            Review, uuid=reviewUuid, deletedAt__isnull=True
        )

        school = request.user.teachingSchools.first()
        reviewAuthor: User = review.author
        authorSchools = reviewAuthor.schools.first()
        if school != authorSchools:
            return Response(
                data={
                    "detail": "Du har ikke tilladelse til at afvise denne anmeldelse."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        review.deletedAt = timezone.now()
        review.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetWorkplaceReviewsView(CustomAPIView, BasicPageination):
    """
    <GET> returns a paginatied list of workplace reviews
    ?stars=<int>
    """

    serializer_class = ReviewSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        stars = request.GET.get("stars", "all")
        workplaceUuid = kwargs.get("workplaceUuid")
        workplace = get_object_or_404(
            Workplace, uuid=workplaceUuid, deletedAt__isnull=True
        )

        cacheKey = f"workplace:{workplace.pk}:reviews:page:1"
        if stars == "all":
            if self.getPageNumber(request) == 1:
                cachedData = cache.get(cacheKey)
                if cachedData:
                    return Response(data=cachedData, status=status.HTTP_200_OK)

        filter = Q(
            workplace=workplace, deletedAt__isnull=True, verifiedBy__isnull=False
        )
        if stars and stars != "all":
            filter &= Q(stars=stars)

        reviews = Review.objects.filter(filter).order_by("-createdAt")

        paginated = self.paginate(reviews, request)
        if self.getPageNumber(request) == 1 and stars == "all":
            cache.set(cacheKey, paginated.data, timeout=60 * 10)  # Cache for 10 minutes
        return Response(data=paginated.data, status=status.HTTP_200_OK)


class GetCategoriesView(CustomAPIView, BasicPageination):
    """
    <GET> returns a list of workplace categories
    """

    authentication_classes = []
    permission_classes = []

    serializer_class = TopCategorySerializer

    def get(self, request, *args, **kwargs):
        cacheKey = "workplace:categories"
        cachedData = cache.get(cacheKey)
        if cachedData:
            return Response(data=cachedData, status=status.HTTP_200_OK)

        categories = TopCategory.objects.filter(deletedAt__isnull=True).order_by(
            "-name"
        )
        serializer = self.serializer_class(categories, many=True)

        cache.set(cacheKey, serializer.data, timeout=60 * 10)  # Cache for 10 minutes
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GetCategoryView(CustomAPIView):
    """
    <GET> returns a category by uuid
    """

    authentication_classes = []
    permission_classes = []

    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        categoryUuid = kwargs.get("categoryUuid")
        category = get_object_or_404(
            Category, uuid=categoryUuid, deletedAt__isnull=True
        )
        serializer = self.serializer_class(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
