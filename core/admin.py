from django.contrib import admin
from .models import CustomPermission, UserGroup

# Register your models here.

admin.site.register(CustomPermission)
admin.site.register(UserGroup)
