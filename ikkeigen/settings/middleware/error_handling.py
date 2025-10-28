import os
import traceback

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext as _
from rest_framework import exceptions, status, views
from rest_framework.generics import UpdateAPIView
from users.auth import CustomTokenAuthentication
from users.permissions import UserPermissions

from .decrytper import RequestTimeLoggingMiddleware


def sendDiscordMessage(message):
    url = str(os.getenv("DISCORD_WEBHOOK_URL"))
    if not url or url == "":
        return

    data = {"content": message}
    requests.post(url, json=data)


class GlobalExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        user = getattr(request, "user", None)
        sendDiscordMessage(
            "**Global exception caught:**\n"
            + str(exception)
            + "\n\nUser: "
            + str(user)
            + "\nPath: "
            + str(request.path)
            + "\nMethod: "
            + str(request.method)
            + "\n\n*Traceback:* \n```"
            + traceback.format_exc()
            + "```"
        )
        return None


class CustomAPIView(UserPermissions, RequestTimeLoggingMiddleware):
    authentication_classes = (CustomTokenAuthentication,)
    authenticationRequired = True
    allowUnacceptedPrivacyPolicy = False
    roleNeeded = None
    noPermissionForMethods = []

    def __init__(self, **kwargs) -> None:
        if self.authenticationRequired == False:
            self.permission_classes = ()
        super().__init__(**kwargs)

    @property
    def language(self):
        """
        Returns the language code from the request.
        """
        return self.request.headers.get("Accept-Language", settings.LANGUAGE_DEFAULT)

    def raise_uncaught_exception(self, exception):
        account = self.request.user
        sendDiscordMessage(
            "**Uncaught exception:**\n"
            + str(exception)
            + "\n\n\nUser: "
            + str(account)
            + "\nPath: "
            + str(self.request.path)
            + "\nMethod: "
            + str(self.request.method)
            + "\n\n\n*Traceback:* "
            + str(traceback.format_exc())
        )
        return super().raise_uncaught_exception(exception)

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        return [
            auth(authenticationRequired=self.authenticationRequired)
            for auth in self.authentication_classes
        ]


class CustomUpdateAPIView(UpdateAPIView, CustomAPIView):
    authentication_classes = (CustomTokenAuthentication,)


def custom_exception_handler(exc, context):
    response = views.exception_handler(exc, context)

    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
