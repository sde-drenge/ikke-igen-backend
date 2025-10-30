from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from djangoql.admin import DjangoQLSearchMixin

from .models import Category, Review, Workplace


class CategoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("pk", "name")
    fields = [
        "name",
    ]

    ordering = ("-name",)


class WorkplaceAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("pk", "name", "vat")
    fields = [
        "name",
        "vat",
        "website",
        "allCategories",
        "deletedAt",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    ordering = ("-createdAt",)

    readonly_fields = [
        "allCategories",
        "updatedAt",
        "createdAt",
        "uuid_hex",
    ]

    def uuid_hex(self, obj):
        return obj.uuid.hex

    @mark_safe
    def allCategories(self, obj: Workplace):
        html = "<ul>"

        objs = obj.categories.all()
        for obj in objs:
            html += '<li><a href="{0}">{1}</a></li>'.format(
                reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.id],
                ),
                obj.__str__(),
            )
        return html + "</ul>"

    allCategories.allow_tags = True
    allCategories.short_description = "Categories"


class ReviewAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("pk", "workplace", "author", "stars", "verified")
    fields = [
        "stars",
        "title",
        "comment",
        "author",
        "workplace",
        "verifiedBy",
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

    def verified(self, obj):
        return obj.verifiedBy is not None

    verified.boolean = True
    verified.short_description = "Verified"


admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
