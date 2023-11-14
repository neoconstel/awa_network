"""
URL configuration for core project.

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
from django.contrib import admin
from django.urls import path, include, re_path

# wagtail imports
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

# for staticfile configs
from django.conf import settings

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('auth/', include('user.api.urls')),
    path('api/', include('main.api.urls')),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # this should be last
    re_path(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # --------Serve static and media files from development server-------
    # fixes issue of admin staticfiles missing when served from http://localhost
    urlpatterns += staticfiles_urlpatterns()

    # make it possible to use media_url in frontend to access backend media content
    # (e.g <img src="http://localhost:8000/media/image/meg.jpg" alt="my image"/>)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
