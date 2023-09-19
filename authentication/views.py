from typing import Any, Dict
import datetime

from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from .models import BaseUser, GoogleTokens
from .authentication_class import CustomJWTAuthentication
from core.utils.sdk.google_service import (
    GoogleSdkLoginFlowService,
)
from common.views import PublicApi
from .serializers import InputSerializer, GoogleTokensUpdateSerializer, BaseUserSerializer

###
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.oauth2.credentials


def upload_video(creds):
    '''
    creds:{'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
    '''

    request_body={
        'snippet': {
            'title': 'Test 2',
            'description': 'Test video',
            'categoryId': 1,
            # 'tags': ['tags']
        },
        'status': {
            'privacyStatus': 'private',
            'publishedAt': (datetime.datetime.now()).isoformat(),
            'selfDeclaredMadeForKids': False
        },
        'notifySubscribers': False
    }
    video_file='/Users/mr-palindrome/Work/Personal projects/POC/test1.mp4'
    media_file=MediaFileUpload(video_file).to_json()
    try:
        credentials=google.oauth2.credentials.Credentials(
            **creds)
        youtube=build('youtube', 'v3', credentials=credentials)
        response_video_upload=youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media_file
        ).execute()
        uploaded_video_id=response_video_upload.get('id')
        print(uploaded_video_id)
    except Exception as e:
        print(e)


###

class GoogleOauth:


    def __init__(self):
        self.creds = None
        self.user_info = None

    def save_credentials(self, user: BaseUser, code: str, state: str):
        """
        Save the user's credentials in the GoogleTokens model.
        :param state:
        :param code:
        :param user:
        :return: none
        """
        google_tokens=GoogleTokens(
            user=user,
            access_token=self.creds['token'],
            refresh_token=self.creds['refresh_token'],
            code=code,
            state=state
        )
        google_tokens.save()

    def update_credentials(self, user: BaseUser, code: str, state: str):
        """
        Update the user's credentials in the GoogleTokens model.
        :param state:
        :param code:
        :param user:
        :return: none
        """
        if GoogleTokens.objects.filter(user=user).exists():
            google_tokens=GoogleTokens.objects.get(user=user)
            google_tokens.access_token=self.creds['token']
            google_tokens.refresh_token=self.creds['refresh_token']
            google_tokens.save()
        else:
            self.save_credentials(user, code, state)

    def get_user_jwt_token(self, user_email: str, code: str, state: str):
        """
        Get the JWT token for the user.
        """

        if BaseUser.objects.user_exists(user_email):
            user=BaseUser.objects.get(email=user_email)
            jwt_refresh=RefreshToken.for_user(user)
            msg={
                "refresh": str(jwt_refresh),
                "access": str(jwt_refresh.access_token),
                "signed": True
            }
        else:
            user=BaseUser.objects.create_user(
                email=user_email,
                first_name=self.user_info.get("given_name"),
                last_name=self.user_info.get("family_name"),
                phone_number=self.user_info.get("phone_number"),
                country_code=self.user_info.get("country_code"),
                profile_pic=self.user_info.get("picture"),
            )
            jwt_refresh=RefreshToken.for_user(user)
            msg={
                "refresh_token": str(jwt_refresh),
                "access_token": str(jwt_refresh.access_token),
                "signed": False,"user_info": self.user_info
            }
        self.update_credentials(user, code, state)
        return msg


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow=GoogleSdkLoginFlowService()

        authorization_url, state=google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"]=state
        return redirect(authorization_url)


class GoogleLoginApi(PublicApi, GoogleOauth):

    serializer_class=InputSerializer

    def __init__(self, **kwargs):
        super().__init__()
        self.creds=None
        self.user_info=None
        self.google_tokens=None
        self.google_login_flow=None

    def get(self, request, *args, **kwargs):
        input_serializer=self.serializer_class(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data=input_serializer.validated_data

        code=validated_data.get("code")
        error=validated_data.get("error")
        state=validated_data.get("state")

        if error is not None:
            return Response({"error": error}, status=HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({"error": "Code and state are required."}, status=HTTP_400_BAD_REQUEST)

        session_state=request.session.get("google_oauth2_state")

        if session_state is None:
            return Response({"error": "CSRF check failed."}, status=HTTP_400_BAD_REQUEST)

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response({"error": "CSRF check failed."}, status=HTTP_400_BAD_REQUEST)

        self.google_login_flow=GoogleSdkLoginFlowService()

        self.google_tokens, self.creds=self.google_login_flow.get_tokens(code=code, state=state)

        id_token_decoded=self.google_tokens.decode_id_token()

        self.google_login_flow.get_user_info(google_tokens=self.google_tokens)

        self.user_info=self.google_login_flow.get_user_info(google_tokens=self.google_tokens)

        return Response(self.get_user_jwt_token(user_email=id_token_decoded["email"], code=code, state=state), status=HTTP_200_OK)


class UpdateUserDetailsApi(PublicApi):
    authentication_classes=[CustomJWTAuthentication]
    permission_classes=[IsAuthenticated]

    serializer_class=BaseUserSerializer

    def post(self, request):
        user=request.user
        serializer=self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "User details updated successfully"}, status=HTTP_200_OK)


class CustomTokenRefreshView(PublicApi):
    authentication_classes=[CustomJWTAuthentication]
    permission_classes=[IsAuthenticated]

    def post(self, request):
        try:
            google_login_flow=GoogleSdkLoginFlowService()
            google_token = GoogleTokens.objects.get(user=self.request.user)
            credentials = google_login_flow.refresh_access_token(google_token)

            serializer = GoogleTokensUpdateSerializer(
                google_token,
                data={
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token
                },
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

            jwt_refresh=RefreshToken.for_user(request.user)
            return Response({'access_token': str(jwt_refresh.access_token)}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Token refresh failed'}, status=HTTP_400_BAD_REQUEST)


class LogoutView(PublicApi):
    authentication_classes=[CustomJWTAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self, request):
        # Revoke the Google OAuth token
        # google_tokens = GoogleTokens.objects.get(user=request.user)
        # if google_tokens:
        #     try:
        #         revoke(google_tokens.access_token, google_tokens.refresh_token)
        #     except Exception as e:
        #         return Response({'error': 'Failed to revoke Google OAuth token'}, status=status.HTTP_400_BAD_REQUEST)

        # Expire the JWT token
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except:
                return Response({'error': 'Failed to expire JWT token'}, status=HTTP_400_BAD_REQUEST)

        return Response({'message': 'Logout successful'}, status=HTTP_200_OK)