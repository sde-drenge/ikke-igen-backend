from django.urls import include, re_path
from rest_framework import routers

router = routers.DefaultRouter()

from . import views


def get_urls():
    """Append custom urls"""
    urls = router.urls

    urls.append(
        re_path(
            r"^categories/$",
            views.GetCategoriesView.as_view(),
            name="get_categories",
        )
    )

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
            r"^reviews/(?P<reviewUuid>\w+)/verify/$",
            views.VerifyWorkplaceReviewView.as_view(),
            name="verify_workplace_review",
        )
    )

    urls.append(
        re_path(
            r"^reviews/(?P<reviewUuid>\w+)/decline/$",
            views.DeclineWorkplaceReviewView.as_view(),
            name="decline_workplace_review",
        )
    )

    urls.append(
        re_path(
            r"^(?P<workplaceUuid>\w+)/$",
            views.GetWorkplaceView.as_view(),
            name="get_workplace",
        )
    )

    urls.append(
        re_path(
            r"^(?P<workplaceUuid>\w+)/reviews/$",
            views.GetWorkplaceReviewsView.as_view(),
            name="get_workplace_reviews",
        )
    )

    return urls


urlpatterns = [
    re_path(r"^", include(get_urls())),
]
