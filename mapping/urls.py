from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from mapping import views

urlpatterns = [
    url(r'(?P<req_id>\d+)/map$',views.map, name='map'),
    url(r'(?P<req_id>\d+)/(?P<doc_id>\d+)/(?P<file_accept>\d+)/map2$',views.map2, name='map2'),
    url(r'request/$',views.create_request_form, name='requests'),
    url(r'request/(?P<pk>\d+)/$',views.update_request_form, name='update_requests'),
    url(r'^delete-entry/(?P<pk>\d+)/$', views.delete_template, name='delete_template'),
    url(r'^delete-requests/(?P<pk>\d+)/$', views.delete_requests, name='delete_requests'),
    url(r'template/reqstatus/$',views.reqstatus, name='reqstatus'),
    url(r'template/requestDownload/$',views.requestDownload, name='requestDownload'),
    url(r'(\d+)/template/$',views.create_template_form, name='template')

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

