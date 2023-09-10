from django.contrib.auth.models import Group
from core.models import CustomPermission

# Create custom permissions
can_upload_video, _ = CustomPermission.objects.get_or_create(
    codename='upload_video',
    name='Can upload video',
)

can_delete_video, _ = CustomPermission.objects.get_or_create(
    codename='delete_video',
    name='Can delete video',
)

can_add_metadata, _ = CustomPermission.objects.get_or_create(
    codename='add_metadata',
    name='Can add metadata',
)

can_approve_video, _ = CustomPermission.objects.get_or_create(
    codename='approve_video',
    name='Can approve video',
)

# Create custom groups
admin_group, _ = Group.objects.get_or_create(name='Admin')
owner_group, _ = Group.objects.get_or_create(name='Owner')
editor_group, _ = Group.objects.get_or_create(name='Editor')

# Assign permissions to groups
# admin_group.permissions.set([can_upload_video, can_delete_video, can_add_metadata, can_approve_video])
owner_group.permissions.set([can_delete_video, can_add_metadata, can_approve_video])
editor_group.permissions.set([can_upload_video, can_add_metadata])
