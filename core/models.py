from django.db import models
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel

class CustomPermission(BaseModel):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserGroup(BaseModel):
    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        CustomPermission,
        verbose_name=_("permissions"),
        blank=True,
    )

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")


    def __str__(self):
        return self.name

