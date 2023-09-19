from rest_framework import permissions

class CanUploadVideoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_custom_perm('upload_video')

class CanDeleteVideoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_custom_perm('delete_video')

class CanAddMetadataPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_custom_perm('add_metadata')

class CanApproveVideoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_custom_perm('approve_video')

class CanCreateTeamPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        create_status = request.user and request.user.has_custom_perm('create_team')
        # TODO: create a logic which will verify team creation quota from subscription and change create status accordingly
        return create_status

class IsOwnerOfTeamPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        owner_status =  request.user and request.user.is_owner_of_team(obj)
        # TODO: create a logic which will see if the team is created by the current user of not and change owner status accordingly
        return owner_status

class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_editor