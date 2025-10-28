from django.core.cache import cache
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from schools.models import School
from settings.middleware.error_handling import CustomAPIView
from users.models import User
from users.views import BasicPageination

from .models import Review, Workplace
from .serializers import LightWorkplaceSerializer, ReviewSerializer, WorkplaceSerializer


class SearchWorkPlacesView(CustomAPIView, BasicPageination):
    """
    <GET> returns paginatied list of workplaces
    ?search=<str>
    """

    serializer_class = LightWorkplaceSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "")

        workplaces = Workplace.objects.filter(
            Q(name__icontains=search, deletedAt__isnull=True)
            | Q(vat__icontains=search, deletedAt__isnull=True)
            | Q(website__icontains=search, deletedAt__isnull=True)
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

        if data.get("stars") > 5 or data.get("stars") < 0:
            return Response(
                data={"detail": "Stjerner skal være mellem 0 og 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyWorkplaceReviewView(CustomAPIView):
    """
    <POST> verify a workplace review
    Data: {
        "reviewUuid": "string",
    }
    """

    roleNeeded = "teacher"

    def post(self, request, *args, **kwargs):
        review_uuid = request.data.get("reviewUuid")
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

    roleNeeded = "teacher"
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
