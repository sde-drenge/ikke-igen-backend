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
                    "education",
                    "school",
                    "teacherAtSchhool",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "isActive",
                    "is_staff",
                    "is_superuser",
                    "role",
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
        "school",
        "teacherAtSchhool",
        "verificationCode",
        "uuid_hex",
        "createdAt",
        "updatedAt",
        "deletedAt",
    ]

    def uuid_hex(self, obj):
        return obj.uuid.hex

    @mark_safe
    def school(self, obj: User):
        html = "<ul>"

        objs = [obj.schools.first() if obj.schools.exists() else None]
        for obj in objs:
            html += '<li><a href="{0}">{1}</a></li>'.format(
                reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.id],
                ),
                obj.__str__(),
            )
        return html + "</ul>"

    school.allow_tags = True
    school.short_description = "Student at"

    @mark_safe
    def teacherAtSchhool(self, obj: User):
        html = "<ul>"

        objs = [obj.teachingSchools.first() if obj.teachingSchools.exists() else None]
        for obj in objs:
            html += '<li><a href="{0}">{1}</a></li>'.format(
                reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.id],
                ),
                obj.__str__(),
            )
        return html + "</ul>"

    teacherAtSchhool.allow_tags = True
    teacherAtSchhool.short_description = "Teacher at"


admin.site.register(User, UserAdmin)
