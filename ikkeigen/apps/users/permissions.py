from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView


class UserPermissions(APIView):
    roleNeeded = None

    def check_permissions(self, request):
        requestMethod = request.method
        if requestMethod.lower() not in self.noPermissionForMethods:
            if self.roleNeeded:
                user = request.user
                if not user or not user.is_authenticated:
                    raise PermissionDenied(
                        _("You must be logged in to perform this action.")
                    )

                if user.role != self.roleNeeded and user.role not in self.roleNeeded:
                    raise PermissionDenied(
                        _("You do not have permission to perform this action.")
                    )

        super().check_permissions(request)
