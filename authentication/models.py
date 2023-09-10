from django.contrib.auth.models import (
    AbstractBaseUser,
    Group,
    PermissionsMixin,
    BaseUserManager as BUM
)
from django.db import models

from common.models import BaseModel

# Taken from here:
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
# With some modifications


class BaseUserManager(BUM):
    def create_user(self, email, is_active=True, is_admin=False, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email.lower()), is_active=is_active, is_admin=is_admin)

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            is_active=True,
            is_admin=True,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user

    def user_exists(self, email):
        """
        Check if a user with the given email exists.
        """
        return self.filter(email=self.normalize_email(email)).exists()


class BaseUser(BaseModel, AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    # User level
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    # This should potentially be an encrypted field
    # jwt_key = models.UUIDField(default=uuid.uuid4)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    def is_owner_of_team(self, team):
        """
        Check if the user is the owner of the given team.
        """
        return team.owner == self

    def is_editor_of_team(self, team):
        """
        Check if the user is an editor of the given team.
        """
        return team.editors.filter(id=self.id).exists()

    def get_permissions_for_team(self, team):
        """
        Get permissions for the user within the given team.
        If the user is the owner, return owner permissions.
        If the user is an editor, return editor permissions.
        """
        owner_group = Group.objects.get(name='owner')
        editor_group = Group.objects.get(name='editor')

        if self.is_owner_of_team(team):
            # Return owner permissions associated with the group
            return owner_group.permissions.all()
        elif self.is_editor_of_team(team):
            # Return editor permissions associated with the group
            return editor_group.permissions.all()
        else:
            return None  # User is not associated with the team