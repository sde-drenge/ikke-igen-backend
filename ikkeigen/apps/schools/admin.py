from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from djangoql.admin import DjangoQLSearchMixin
from users.models import User

from .models import School, TeacherInvite


class SchoolAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("pk", "name")
    fields = [
        "name",
        "address",
        "students",
        "teachers",
        "deletedAt",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    ordering = ("-createdAt",)

    readonly_fields = [
        "students",
        "teachers",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    def uuid_hex(self, obj):
        return obj.uuid.hex

    @mark_safe
    def students(self, obj: School):
        html = "<ul>"

        objs = obj.students.all()
        for obj in objs:
            html += '<li><a href="{0}">{1}</a></li>'.format(
                reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.id],
                ),
                obj.__str__(),
            )
        return html + "</ul>"

    students.allow_tags = True
    students.short_description = "Students"

    @mark_safe
    def teachers(self, obj: School):
        html = "<ul>"

        objs = obj.teachers.all()
        for obj in objs:
            html += '<li><a href="{0}">{1}</a></li>'.format(
                reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.id],
                ),
                obj.__str__(),
            )
        return html + "</ul>"

    teachers.allow_tags = True
    teachers.short_description = "Teachers"


class TeacherInviteAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("pk", "email", "school")
    fields = [
        "email",
        "invitedUser",
        "school",
        "invitedBy",
        "accepted",
        "deletedAt",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    ordering = ("-createdAt",)

    readonly_fields = [
        "invitedUser",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    def uuid_hex(self, obj):
        return obj.uuid.hex

    @mark_safe
    def invitedUser(self, obj: TeacherInvite):
        html = "<ul>"

        user = User.objects.filter(email=obj.email, deletedAt__isnull=True).first()
        if not user:
            return f"<li>En bruger med email {obj.email} eksistere ikke</li>"

        objs = [user]
        for obj in objs:
            html += '<li><a href="{0}">{1}</a></li>'.format(
                reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.id],
                ),
                obj.__str__(),
            )
        return html + "</ul>"

    invitedUser.allow_tags = True
    invitedUser.short_description = "Invited User"


admin.site.register(School, SchoolAdmin)
admin.site.register(TeacherInvite, TeacherInviteAdmin)
