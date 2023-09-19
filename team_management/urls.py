from django.urls import path

from .views import TeamViewSet, TeamUpdateView

app_name = 'team_management'

urlpatterns = [
    path('', TeamViewSet.as_view({'get': 'list', 'post': 'create'}), name="list-create"),
    path('<int:pk>/', TeamUpdateView.as_view(), name='team-update'),
]