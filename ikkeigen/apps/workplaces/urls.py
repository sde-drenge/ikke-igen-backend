from django.urls import include, re_path
from rest_framework import routers

router = routers.DefaultRouter()

from . import views


def get_urls():
    """Append custom urls"""
    urls = router.urls

    urls.append(
        re_path(
            r"^find/$",
            views.SearchWorkPlacesView.as_view(),
            name="search_workplaces",
        )
    )

    urls.append(
        re_path(
            r"^create/$",
            views.CreateWorkPlaceView.as_view(),
            name="create_workplace",
        )
    )

    urls.append(
        re_path(
            r"^(?P<workplaceUuid>\w+)/$",
            views.GetWorkplaceView.as_view(),
            name="get_workplace",
        )
    )

    return urls


urlpatterns = [
    re_path(r"^", include(get_urls())),
]
