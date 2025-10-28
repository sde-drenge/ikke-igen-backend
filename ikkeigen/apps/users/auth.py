import jwt
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import authentication, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission

from .models import User


class CustomTokenAuthentication(authentication.BaseAuthentication):
    """
    Add this header:
    Authorization: Token <Token>
    """

    keyword = "Token"
    model = None
    authenticationRequired = True

    def __init__(self, authenticationRequired=True):
        self.authenticationRequired = authenticationRequired

    def authenticate(self, request):
        jwtKey = request.COOKIES.get("jwt")

        if jwtKey is None:
            jwtKey = authentication.get_authorization_header(request).split()
            if jwtKey is None or len(jwtKey) != 2:
                return None

            if jwtKey[0].decode() != self.keyword:
                return None
            jwtKey = jwtKey[1]

        try:
            userDetails = jwt.decode(jwtKey, settings.SECRET_KEY, algorithms="HS256")
        except Exception as e:
            if self.authenticationRequired:
                msg = _("Invalid Token")
                raise exceptions.AuthenticationFailed(msg)
            else:
                return (None, None)

        if (
            not userDetails
            or not userDetails.get("user_id")
            or not userDetails.get("token")
        ):
            msg = _("Invalid Login Credentials")
            raise exceptions.AuthenticationFailed(msg)

        user: User = User.objects.filter(id=userDetails.get("user_id")).first()
        if not user:
            msg = _("Invalid Login Credentials")
            raise exceptions.AuthenticationFailed(msg)

        if not user.isActive:
            msg = _("User is not verified")
            raise exceptions.AuthenticationFailed(msg)

        userToken = Token.objects.filter(user=user).first()
        if not userToken:
            msg = _("Invalid Token")
            raise exceptions.AuthenticationFailed(msg)

        token = userDetails.get("token")
        if token != userToken.key:
            msg = _("Invalid Token")
            raise exceptions.AuthenticationFailed(msg)

        if user.deletedAt is not None:
            msg = _(
                "This user has been deleted. Please contact support for more information"
            )
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
