from django.contrib import admin

# Register your models here.

from .models import Requests, Template, Response, ResponseFile

admin.site.register(Requests)
admin.site.register(Template)
admin.site.register(Response)
admin.site.register(ResponseFile)
