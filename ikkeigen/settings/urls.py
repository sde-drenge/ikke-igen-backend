"""
URL configuration for ticketsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^documentation/schema/$",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    re_path(
        r"^documentation/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    # My Paths
    re_path(r"^users/", include(("users.urls", "user"), namespace="user")),
    re_path(r"^schools/", include(("schools.urls", "schools"), namespace="schools")),
    re_path(
        r"^workplaces/",
        include(("workplaces.urls", "workplaces"), namespace="workplaces"),
    ),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(
    settings.IKKEIGEN_STATIC_URL, document_root=settings.IKKEIGEN_STATIC_DIR
)
