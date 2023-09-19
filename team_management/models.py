from django.db import models

from authentication.models import BaseUser
from common.models import BaseModel
# Create your models here.

class Team(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(BaseUser, null=False, blank=False, on_delete=models.CASCADE, related_name='owned_teams')
    editors = models.ManyToManyField(BaseUser, related_name='teams', null=True, blank=True)

    # invitations = models.ManyToManyField('Invitation', related_name='team_invitations')

    def __str__(self):
        return self.name

class Invitation(models.Model):
    email = models.EmailField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    token = models.CharField(max_length=64, unique=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email