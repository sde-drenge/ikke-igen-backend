from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from djangoql.admin import DjangoQLSearchMixin

from .models import School


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


admin.site.register(School, SchoolAdmin)
