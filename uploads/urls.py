from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as authviews
from uploads.core import views
from uploads.core.forms import LoginForm


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'signup/$', views.SignUp.as_view(), name='signup'),
    url(r'^uploads/form/$', views.model_form_upload, name='model_form_upload'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
    {'next_page': '/logged_out/'}),
    url(r'^logged_out/$', views.logged_out, name='logged_out'),
    url(r'^login/$', authviews.login, {'authentication_form':LoginForm}),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'mapping/', include('mapping.urls')),
    url(r'^admin/', admin.site.urls)

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

