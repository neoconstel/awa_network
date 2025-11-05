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

# for serving media files while in development
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# for loading the entry html template
from django.views.generic import TemplateView

from user.wagtail.api.viewsets import api_router

# for staticfile configs
from django.conf import settings

urlpatterns = [
    re_path(r'^django-admin/*', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # ✅ Required for login/logout routes (for google glient)
    re_path(r'^auth/*', include('user.api.urls')),
    re_path(r'^api/*', include('main.api.urls')),
    re_path(r'^resource/*', include('main.api.urls')),

    re_path(r'^admin/*', include(wagtailadmin_urls)),
    re_path(r'documents/*', include(wagtaildocs_urls)),

    # filepond
    re_path(r'^fp/*', include('django_drf_filepond.urls')),

    # # WAGTAIL API ENDPOINTS (pages, images, documents)
    re_path(r'api/v2/*', api_router.urls),

    # the frontend urlpattern is added LAST, after staticfiles_urlpatterns.
    # otherwise it would block media urlpatterns and disable display of media
]

if settings.DEBUG:
    # --------Serve static and media files from development server-------
    # fixes issue of admin staticfiles missing when served from http://localhost
    urlpatterns += staticfiles_urlpatterns()

    # make it possible to use media_url in frontend to access backend media content
    # (e.g <img src="http://localhost:8000/media/image/meg.jpg" alt="my image"/>)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    # this should be last (if not using an external frontend like vue)
    re_path(r'^[^/].+', include(wagtail_urls)),

    # This should be the VERY LAST! (for routung unknown urls to the frontend)
    re_path('', TemplateView.as_view(template_name="main/home_page.html"))
]
