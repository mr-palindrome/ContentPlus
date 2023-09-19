from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager as BUM
)
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from common.models import BaseModel
from core.models import UserGroup

# Taken from here:
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
# With some modifications


class BaseUserManager(BUM):
    def create_user(self, email, is_active=True, is_admin=False, password=None, *args, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email.lower()), is_active=is_active, is_admin=is_admin, **kwargs)

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name = None, password=None):
        if first_name is None:
            first_name = email
        user = self.create_user(
            email=email,
            is_active=True,
            is_admin=True,
            password=password,
            first_name=first_name
        )

        user.is_superuser = True
        # user.save(using=self._db)

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
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=True)

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

    def has_custom_perm(self, perm, obj=None):
        if self.is_owner:
            return UserGroup.objects.get(name='Owner').permissions.filter(codename=perm).exists()
        elif self.is_editor:
            return UserGroup.objects.get(name='Editor').permissions.filter(codename=perm).exists()
        elif self.is_admin:
            return True
        else:
            return False

    def has_perm(self, obj=None):
        return self.is_admin


    def has_module_perms(self, app_label):
        return self.is_admin

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
        owner_group = UserGroup.objects.get(name='owner')
        editor_group = UserGroup.objects.get(name='editor')

        if self.is_owner_of_team(team):
            # Return owner permissions associated with the group
            return owner_group.permissions.all()
        elif self.is_editor_of_team(team):
            # Return editor permissions associated with the group
            return editor_group.permissions.all()
        else:
            return None  # User is not associated with the team

    def save(self, *args, **kwargs):
        if self.is_owner and self.is_editor:
            raise ValidationError("A user cannot be both an owner and an editor.")

        super().save(*args, **kwargs)


class GoogleTokens(BaseModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=False, blank=False)
    refresh_token = models.CharField(max_length=255, null=False, blank=False)
    state = models.CharField(max_length=255, null=False, blank=False)
    code = models.CharField(max_length=255, null=False, blank=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        current_time = timezone.now()
        if self.expires_at < current_time:
            return f"{self.user.email} - expired"
        remaining_time = (self.expires_at - current_time).total_seconds() / 60

        return f"{self.user.email} - {remaining_time:.2f} "

    def save(self, *args, **kwargs):
        # Calculate the expiration time (59 minutes from the updated_time)
        expiration_time = timezone.now() + timezone.timedelta(minutes=59)
        self.expires_at = expiration_time
        super().save(*args, **kwargs)
