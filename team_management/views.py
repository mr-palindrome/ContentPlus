from django.shortcuts import render
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.shortcuts import redirect

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from .models import Team, Invitation
from .serializers import TeamSerializer
from common.models import BaseModel
from common.views import PublicApi, PublicUpdateApi
from core.permissions import CanCreateTeamPermission, IsOwnerOfTeamPermission
from authentication.authentication_class import CustomJWTAuthentication

# Create your views here.


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, CanCreateTeamPermission, IsOwnerOfTeamPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Team.objects.all()
        else:
            return Team.objects.filter(Q(owner=user) | Q(editors=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TeamUpdateView(PublicUpdateApi):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOfTeamPermission]

    def perform_update(self, serializer):
        # Automatically set the owner to the current user
        serializer.save()

class InviteUserToTeamView(PublicApi):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOfTeamPermission]

    def post(self, request, team_id):
        # Assuming 'email' contains the invited user's email address
        email = request.data.get('email')

        # Generate a unique token
        token = get_random_string(length=32)

        # Create an invitation
        invitation = Invitation.objects.create(email=email, token=token, team_id=team_id)

        # Send an email with the invitation link
        # Modify this to suit your email sending logic
        send_mail(
            'Invitation to join the team',
            f'You have been invited to join the team. Click here to accept the invitation: http://localhost:8000/?token={invitation.token}',
            request.user.email,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Invitation sent successfully.'}, status=HTTP_201_CREATED)


class RegistrationView(PublicApi):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.is_owner:
            return Response({'message':'Owner can not join a team.'}, status=HTTP_400_BAD_REQUEST)
        token = request.query_params.get('token')

        # Validate the token
        invitation = get_object_or_404(Invitation, token=token, accepted=False)

        # If the token is valid, accept the invitation
        # Add your logic here to associate the user with the team
        team = invitation.team
        team.editors.add(request.user)


        # Mark the invitation as accepted
        invitation.accepted = True
        invitation.save()

        # Redirect to your registration page
        return redirect('https://app.contentplus.com/')

