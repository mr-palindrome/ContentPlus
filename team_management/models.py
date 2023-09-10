from django.db import models

from authentication.models import BaseUser
from common.models import BaseModel
# Create your models here.

class Team(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(BaseUser, null=False, blank=False, on_delete=models.CASCADE, related_name='owned_teams')
    editors = models.ManyToManyField(BaseUser, related_name='teams')

    def __str__(self):
        return self.name