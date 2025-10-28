from django.urls import include, re_path
from rest_framework import routers

router = routers.DefaultRouter()

from . import views


def get_urls():
    """Append custom urls"""
    urls = router.urls

    urls.append(
        re_path(
            r"^signup/$",
            views.SignUpView.as_view(),
            name="signup_view",
        )
    )

    urls.append(
        re_path(
            r"^login/$",
            views.LoginView.as_view(),
            name="login_view",
        )
    )

    urls.append(
        re_path(
            r"^verify-user/(?P<userUuid>\w+)/$",
            views.VerifyUserView.as_view(),
            name="verify_user_view",
        )
    )

    urls.append(
        re_path(
            r"^update/$",
            views.UpdateUserView.as_view(),
            name="update_user_view",
        )
    )

    return urls


urlpatterns = [
    re_path(r"^", include(get_urls())),
]
