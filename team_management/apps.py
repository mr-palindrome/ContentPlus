from django.apps import AppConfig


class TeamManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team_management'

class ApiConfig(AppConfig):
    name = "contentplus_backend.team_management"
