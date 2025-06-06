"""
URL configuration for agriapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("", include("home.urls", namespace="home.urls")),
    path("discussions/", include("discussions.urls", namespace="discussions")),
    path("disease/", include("disease_predictor.urls", namespace="disease_predictor")),
    path('accounts/', include('django.contrib.auth.urls')),
]
# Serve media files during development (IMPORTANT: NOT FOR PRODUCTION)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)