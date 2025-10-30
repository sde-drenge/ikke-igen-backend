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
            views.SearchSchoolsView.as_view(),
            name="search_schools",
        )
    )

    urls.append(
        re_path(
            r"^education-types/find/$",
            views.SearchEducationView.as_view(),
            name="search_education",
        )
    )

    urls.append(
        re_path(
            r"^my-school/teachers/$",
            views.GetTeachersFromSchoolView.as_view(),
            name="get_teachers_from_school",
        )
    )

    urls.append(
        re_path(
            r"^add-teacher/$",
            views.AddTeacherToSchool.as_view(),
            name="add_teacher_to_school",
        )
    )

    urls.append(
        re_path(
            r"^teachers/(?P<userUuid>\w+)/remove/$",
            views.RemoveTeacherFromSchool.as_view(),
            name="remove_teacher_from_school",
        )
    )

    urls.append(
        re_path(
            r"^(?P<inviteUuid>\w+)/is-teacher/$",
            views.CheckIfTeacherAtSchoolView.as_view(),
            name="check_if_teacher_at_school",
        )
    )

    urls.append(
        re_path(
            r"^(?P<inviteUuid>\w+)/accept/$",
            views.AcceptInviteView.as_view(),
            name="accept_invite",
        )
    )

    return urls


urlpatterns = [
    re_path(r"^", include(get_urls())),
]
