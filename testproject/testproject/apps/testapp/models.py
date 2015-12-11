from __future__ import unicode_literals

from django.db import models


class Model1(models.Model):
    field1 = models.CharField(max_length=42)
