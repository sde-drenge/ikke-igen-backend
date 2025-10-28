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
            r"^(?P<workplaceUuid>\w+)/review/$",
            views.RequestWorkplaceReviewView.as_view(),
            name="review_workplace",
        )
    )

    urls.append(
        re_path(
            r"^unverified-reviews/$",
            views.GetUnverifiedReviewsView.as_view(),
            name="get_unverified_reviews",
        )
    )

    urls.append(
        re_path(
            r"^verify-review/$",
            views.VerifyWorkplaceReviewView.as_view(),
            name="verify_workplace_review",
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
