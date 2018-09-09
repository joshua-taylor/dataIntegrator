from __future__ import unicode_literals
from django.conf import settings
from django.db import models
import datetime


class Requests(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=40, blank=True)
    desc = models.CharField(max_length=255, blank=True)
    send_to = models.CharField(max_length=2048, blank=False)
    status = models.CharField(max_length=10, default='DRAFT', blank=False) # DRAFT ACTIVE CLOSED
    deadline_date = models.DateField(("Deadline"), default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)

class Template(models.Model):
    Request = models.ForeignKey(
        Requests,
        on_delete=models.CASCADE,
    )
    field_name = type = models.CharField(max_length=64, blank=False)
    type = models.CharField(max_length=20, blank=False)
    desc = models.CharField(max_length=255, blank=True)
    max_len = models.IntegerField(blank=False)
    manditory = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)


# This is the field level detail for a response. It links to a request and sits side-by-side with a template.
class Response(models.Model):
    Request = models.ForeignKey(
        Requests,
        on_delete=models.CASCADE,
    )
    creator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='DRAFT', blank=False) # DRAFT ACTIVE CLOSED
    mapped_field_name = models.CharField(max_length=64, blank=False)
    field_name = type = models.CharField(max_length=64, blank=False)
    type = models.CharField(max_length=64, blank=False)
    desc = models.CharField(max_length=255, blank=True)
    max_len = models.IntegerField(blank=False)
    manditory = models.BooleanField()

#This is essentially the header file for a response but it also contains the file itself:
class ResponseFile(models.Model):
    Request = models.ForeignKey(
        Requests,
        on_delete=models.CASCADE,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    rows = models.IntegerField(blank=True,null=True)
    badRows = models.IntegerField(blank=True,null=True)
    documentPath = models.CharField(max_length=255, blank=True,null=True)
    document = models.FileField(null=True, blank=True)
    type = models.CharField(max_length=10, default='RESPONSE', blank=False) #used to determine if response file or if created by owner RESPONSE or DOWNLOAD
    created_at = models.DateTimeField(auto_now_add=True)
