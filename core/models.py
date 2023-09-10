from django.db import models
from django.contrib.auth.models import Permission

from authentication.models import BaseUser
from common.models import BaseModel

class CustomPermission(BaseModel):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name




