
from django import forms
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView

from common.utils.sdk.google_service import (
    GoogleSdkLoginFlowService,
)
from authentication.serializers import InputSerializer
# from styleguide_example.users.selectors import user_list

###
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.oauth2.credentials
import datetime

def upload_video(creds):

    request_body = {
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
    video_file = '/Users/mr-palindrome/Work/Personal projects/POC/test1.mp4'
    media_file = MediaFileUpload(video_file).to_json()
    try:
        credentials = google.oauth2.credentials.Credentials(
            **creds)
        youtube = build('youtube', 'v3', credentials=credentials)
        response_video_upload = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media_file
        ).execute()
        uploaded_video_id = response_video_upload.get('id')
        print(uploaded_video_id)
    except Exception as e:
        print(e)


###

class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()

class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleSdkLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state
        print("current state:",state)

        return redirect(authorization_url)


class GoogleLoginApi(PublicApi):

    serializer_class = InputSerializer
    def get(self, request, *args, **kwargs):
        input_serializer = self.serializer_class(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return JsonResponse({"error": error}, status=400)

        if code is None or state is None:
            return JsonResponse({"error": "Code and state are required."}, status=400)

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return JsonResponse({"error": "CSRF check failed."}, status=400)

        del request.session["google_oauth2_state"]

        if state != session_state:
            return JsonResponse({"error": "CSRF check failed."}, status=400)

        google_login_flow = GoogleSdkLoginFlowService()

        google_tokens, creds = google_login_flow.get_tokens(code=code, state=state)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]
        # upload_video(creds)
        # request_user_list = user_list(filters={"email": user_email})
        # user = request_user_list.get() if request_user_list else None

        # if user is None:
        #     return JsonResponse({"error": f"User with email {user_email} is not found."}, status=404)

        # login(request, user)

        result = {
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
        }

        return JsonResponse(result, status=200)

class GoogleLoginState(PublicApi):

    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleSdkLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state
        print("current state:", state)
        return JsonResponse({'Current State:':str(state)})