from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from settings.middleware.error_handling import CustomAPIView
from users.models import User
from users.views import BasicPageination

from .constants import EDUCATION_TYPES
from .models import School
from .serializers import SchoolSerializer


class AddTeacherToSchool(CustomAPIView, BasicPageination):
    """
    <POST> Adds the user as teacher on the given school.
    schoolUuid in the url params.
    Data: {
        "userUuid": str,
    }
    """

    roleNeeded = "teacher"
    serializer_class = None

    def post(self, request, *args, **kwargs):
        user: User = request.user
        schoolUuid = kwargs.get("schoolUuid")
        school: School = get_object_or_404(
            School, uuid=schoolUuid, deletedAt__isnull=True
        )

        if not school.teachers.filter(uuid=user.uuid, deletedAt__isnull=True).exists():
            return Response(
                {"detail": "Du er ikke en lærer på denne skole."},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = request.data
        userUuid = data.get("userUuid")
        if not userUuid:
            return Response(
                {"detail": "Brugeren blev ikke fundet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        newTeacher: User = get_object_or_404(
            User, uuid=userUuid, deletedAt__isnull=True, isActive=True
        )
        school.teachers.add(newTeacher)
        school.save()
        return Response(
            {"detail": "Brugeren er nu tilføjet som lærer på skolen."},
            status=status.HTTP_200_OK,
        )


class SearchSchoolsView(CustomAPIView, BasicPageination):
    """
    <GET> returns paginatied list of workplaces
    ?search=<str>
    """

    serializer_class = SchoolSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "")

        schools = School.objects.filter(
            Q(name__icontains=search, deletedAt__isnull=True)
        )

        paginated = self.paginate(schools, request)
        return Response(data=paginated.data, status=status.HTTP_200_OK)


class SearchEducationView(CustomAPIView):
    """
    <GET> returns paginatied list of workplaces
    ?search=<str>
    """

    serializer_class = SchoolSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "").lower()

        results = [
            edu_type for edu_type in EDUCATION_TYPES if search in edu_type.lower()
        ]

        return Response(data=results, status=status.HTTP_200_OK)
