from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from djangoql.admin import DjangoQLSearchMixin

from .models import User


# class UserAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
class UserAdmin(DjangoQLSearchMixin, BaseUserAdmin):
    search_fields = [
        "__str__",
        "email",
        "uuid_hex",
    ]
    list_display = (
        "__str__",
        "getFullName",
        "isActive",
        "createdAt",
        "last_login",
    )
    ordering = ("-createdAt",)

    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            _("Personal info"),
            {
                "fields": (
                    "firstName",
                    "lastName",
                    "email",
                    "verificationCode",
                    "profileColor",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "isActive",
                    "isStaff",
                    "is_superuser",
                    "uuid_hex",
                ),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login",)},
        ),
    )

    readonly_fields = [
        "password",
        "verificationCode",
        "uuid_hex",
        "createdAt",
        "updatedAt",
        "deletedAt",
    ]

    def uuid_hex(self, obj):
        return obj.uuid.hex


admin.site.register(User, UserAdmin)
