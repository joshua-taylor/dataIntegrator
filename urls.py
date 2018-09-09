from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import TemplateView
from django.conf.urls.static import static



urlpatterns = [
    url(r'^/', include('uploads.urls')), #includes core urls like user sign up etc...
    url(r'^mapping/', include('mapping.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

