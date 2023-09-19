from django.contrib import admin
from .models import BaseUser, GoogleTokens

# Register your models here.

admin.site.register(BaseUser)
admin.site.register(GoogleTokens)
