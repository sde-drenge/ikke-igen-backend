from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from settings.middleware.error_handling import CustomAPIView
from users.models import User
from users.serializers import LightUserSerializer
from users.utils import sendSchoolInviteEmail
from users.views import BasicPageination

from .constants import EDUCATION_TYPES
from .models import School, TeacherInvite
from .serializers import SchoolSerializer


class GetTeachersFromSchoolView(CustomAPIView, BasicPageination):
    """
    <GET> returns paginatied list of teachers at the school from where the user is teacher.
    """

    roleNeeded = ["teacher", "teacher-admin"]
    serializer_class = LightUserSerializer

    def get(self, request, *args, **kwargs):
        user: User = request.user
        school = user.teachingSchools.first()

        if not school:
            return Response(
                {"detail": "Du er ikke lærer på nogen skoler."},
                status=status.HTTP_403_FORBIDDEN,
            )

        teachers = school.teachers.filter(
            deletedAt__isnull=True, isActive=True, role__in=["teacher", "teacher-admin"]
        )

        paginated = self.paginate(teachers, request)
        return Response(data=paginated.data, status=status.HTTP_200_OK)


class RemoveTeacherFromSchool(CustomAPIView):
    """
    <delete> Removes the user as teacher on the given school from where the user is teacher.
    userUuid in the url params.
    """

    roleNeeded = "teacher-admin"
    serializer_class = None

    def delete(self, request, *args, **kwargs):
        user: User = request.user
        school: School = user.teachingSchools.first()

        if not school:
            return Response(
                {"detail": "Du er ikke en lærer på denne skole."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.role == "teacher-admin":
            return Response(
                {"detail": "Du har ikke tilladelse til at fjerne lærere."},
                status=status.HTTP_403_FORBIDDEN,
            )

        userUuid = kwargs.get("userUuid")
        teacherToRemove: User = get_object_or_404(
            User, uuid=userUuid, deletedAt__isnull=True, isActive=True
        )
        if not school.teachers.filter(
            uuid=teacherToRemove.uuid, deletedAt__isnull=True
        ).exists():
            return Response(
                {"detail": "Brugeren er ikke lærer på skolen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school.teachers.remove(teacherToRemove)
        school.save()

        teacherToRemove.role = "student"
        teacherToRemove.save()

        return Response(
            {"detail": "Brugeren er nu fjernet som lærer på skolen."},
            status=status.HTTP_200_OK,
        )


class AddTeacherToSchool(CustomAPIView):
    """
    <POST> Adds the user as teacher on the given school from where the user is teacher.
    Data: {
        "email": <str>,
    }
    """

    roleNeeded = ["teacher", "teacher-admin"]
    serializer_class = None

    def post(self, request, *args, **kwargs):
        user: User = request.user
        school = user.teachingSchools.first()

        if not school:
            return Response(
                {"detail": "Du er ikke en lærer på denne skole."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        userEmail = data.get("email")
        if not userEmail:
            return Response(
                {"detail": "Brugeren blev ikke fundet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        newTeacher: User = User.objects.filter(
            email=userEmail, deletedAt__isnull=True, isActive=True
        ).first()

        if newTeacher:
            if school.teachers.filter(
                uuid=newTeacher.uuid, deletedAt__isnull=True
            ).exists():
                return Response(
                    {"detail": "Brugeren er allerede lærer på skolen."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        teacherInvite = TeacherInvite.objects.create(
            email=userEmail,
            school=school,
            invitedBy=user,
        )
        sendSchoolInviteEmail(teacherInvite)

        return Response(
            {"detail": "Brugeren er nu inviteret som lærer på skolen."},
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


class CheckIfTeacherAtSchoolView(CustomAPIView):
    """
    <GET> Check if the user is already a teacher at the school the invite is for.
    inviteUuid in the url params.
    """

    def get(self, request, *args, **kwargs):
        user: User = request.user
        inviteUuid = kwargs.get("inviteUuid")
        teacherInvite: TeacherInvite = get_object_or_404(
            TeacherInvite, uuid=inviteUuid, deletedAt__isnull=True
        )

        school: School = teacherInvite.school

        isTeacher = school.teachers.filter(
            uuid=user.uuid, deletedAt__isnull=True
        ).exists()
        if not isTeacher:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            status=status.HTTP_200_OK,
        )


class AcceptInviteView(CustomAPIView):
    """
    <POST> Accept the teacher invite and add the user as a teacher on the school.
    inviteUuid in the url params.
    """

    def post(self, request, *args, **kwargs):
        user: User = request.user
        inviteUuid = kwargs.get("inviteUuid")
        teacherInvite: TeacherInvite = get_object_or_404(
            TeacherInvite,
            uuid=inviteUuid,
            email=user.email,
            accepted=False,
            deletedAt__isnull=True,
        )

        school: School = teacherInvite.school

        if school.teachers.filter(uuid=user.uuid, deletedAt__isnull=True).exists():
            return Response(
                {"detail": "Du er allerede lærer på denne skole."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school.teachers.add(user)
        school.save()

        teacherInvite.accepted = True
        teacherInvite.save()

        user.role = "teacher"
        user.save()

        return Response(
            {"detail": "Du er nu tilføjet som lærer på skolen."},
            status=status.HTTP_200_OK,
        )
