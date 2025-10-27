from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin

from .models import Workplace


class WorkplaceAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("pk", "name", "vat")
    fields = [
        "name",
        "vat",
        "website",
        "deletedAt",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    ordering = ("-createdAt",)

    readonly_fields = [
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    def uuid_hex(self, obj):
        return obj.uuid.hex


admin.site.register(Workplace, WorkplaceAdmin)
