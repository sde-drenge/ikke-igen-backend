from collections import OrderedDict
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from schools.models import School
from settings.middleware.error_handling import CustomAPIView

from .models import User
from .serializers import UserCreatorSerializer, UserSerializer
from .utils import generateVerificationId


class BasicPageination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 500

    def get_paginated_response(self, data):
        current_page = self.page.number

        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", current_page + 1 if self.page.has_next() else None),
                    (
                        "previous",
                        current_page - 1 if self.page.has_previous() else None,
                    ),
                    ("results", data),
                ]
            )
        )

    def paginate(self, queryset, request, context=None, **args):
        page = self.paginate_queryset(queryset.distinct(), request)
        if page is not None:
            context = context or {}
            context["request"] = request
            if not context.get("userUuid"):
                if request.user.is_authenticated:
                    context["userUuid"] = request.user.uuid

            serializer = self.serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        return self.get_paginated_response([])

    def paginateSpecificSerializer(
        self, queryset, request, serializerClass, context=None, **args
    ):
        page = self.paginate_queryset(queryset.distinct(), request)
        if page is not None:
            context = context or {}
            if not context.get("userUuid"):
                if request.user.is_authenticated:
                    context["userUuid"] = request.user.uuid

            serializer = serializerClass(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        return self.get_paginated_response([])


@method_decorator(csrf_exempt, name="dispatch")
class SignUpView(CustomAPIView):
    """
    Post Data:
    {
        "email": "email",
        "password": "password",
        "password2": "password2",
    }
    """

    permission_classes = ()
    authentication_classes = ()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        inputData = request.data

        password = inputData.get("password")
        password2 = inputData.get("password2")
        provider = inputData.get("provider", "password")

        if not password and provider == "password":
            data = {"error": "Password er påkrævet"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if password != password2 or not password:
            data = {"error": "Adgangskoderne stemmer ikke overens"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserCreatorSerializer(data=inputData)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user: User = serializer.instance
            user.set_password(password)

            user.verificationCode = generateVerificationId()

            user.save()
            responseData = self.serializer_class(user).data
            return Response(responseData, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "Noget gik galt. Prøv igen senere", "extra": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(CustomAPIView):
    """
    Post Data:
    {
        "email": "email",
        "password": "password",
    }
    """

    permission_classes = ()
    authentication_classes = ()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        inputData = request.data
        user: User = get_object_or_404(
            User, email__iexact=inputData.get("email"), deletedAt__isnull=True
        )
        if not user.check_password(inputData.get("password")):
            data = {"error": "Forkert email eller adgangskode"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not user.isActive:
            return Response(
                {"error": "Brugeren er ikke verificeret", "uuid": user.uuid.hex},
                status=status.HTTP_200_OK,  # status code 200 because the frontend needs code 200 to use data from the response
                # And they need the uuid to verify the user later
            )

        token = Token.objects.filter(user=user).first()
        if not token:
            token = Token.objects.create(user=user)
        payload = {
            "user_id": user.id,
            "exp": datetime.now() + timedelta(days=1),
            "iat": datetime.now(),
            "token": token.key,
        }
        jwtToken = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        responseData = self.serializer_class(user).data
        responseData["jwtToken"] = jwtToken
        user.updateLastLogin()
        return Response(data=responseData, status=status.HTTP_200_OK)


class VerifyUserView(CustomAPIView):
    """
    Verify The user with the verification code sent via email
    Post Data:
    {
        "verifyCode": "code",
    }
    """

    permission_classes = ()
    authentication_classes = ()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        userUuid = kwargs.get("userUuid")
        user: User = get_object_or_404(User, uuid=userUuid)
        data = request.data
        verifyCode = data.get("verifyCode", "").lower()

        if user.isActive:
            return Response(
                data={"error": "Brugeren er allerede verificeret"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        userVerifyId = user.verificationCode
        if not userVerifyId.lower() == verifyCode:
            return Response(
                data={"error": "Den bekræftelseskode er forkert. Prøv venligst igen"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.isActive = True
        user.verificationCode = None
        user.save()

        token = Token.objects.create(user=user)
        payload = {
            "user_id": user.id,
            "exp": datetime.now() + timedelta(days=1),
            "iat": datetime.now(),
            "token": token.key,
        }
        jwtToken = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        responseData = self.serializer_class(user).data
        responseData["jwtToken"] = jwtToken
        return Response(data=responseData, status=status.HTTP_200_OK)


class UpdateUserView(
    CustomAPIView,
):
    """
    Patch Data:
    {
        "email": "email,
        "firstName": "Fornavn",
        "lastName": "Efter navn",
        "phoneNumber": "number (optional)",
        "schoolUuid": "school uuid (optional)",
        "education": "education (optional)",
    }
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    allowUnacceptedPrivacyPolicy = True

    def patch(self, request, *args, **kwargs):
        user = request.user
        inputData = request.data

        school = None
        if inputData.get("schoolUuid"):
            school = get_object_or_404(
                School, uuid=inputData.get("schoolUuid"), deletedAt__isnull=True
            )

        serializer = self.serializer_class(user, data=inputData, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            if school:
                instance: User = serializer.instance
                school.students.add(instance)
                school.save()

            return Response(serializer.data)
        return Response(
            {"error": serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST
        )
