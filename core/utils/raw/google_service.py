from random import SystemRandom
from typing import Any, Dict
from urllib.parse import urlencode

import jwt
import requests
from attrs import define
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET

from common.utils.exceptions import ApplicationError


@define
class GoogleRawLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


@define
class GoogleAccessTokens:

    id_token: str
    access_token: str
    refresh_token: str

    def decode_id_token(self) -> Dict[str, str]:
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token


class GoogleRawLoginFlowService:
    # API_URI = reverse_lazy("Authentication:google-oauth2:login-raw:callback-raw")
    API_URI = reverse_lazy("authentication:google-oauth2:callback-raw")

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_ACCESS_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    GOOGLE_REFRESH_ACCESS_TOKEN_URL = "https://oauth2.googleapis.com/token"

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtubepartner',
        'https://www.googleapis.com/auth/youtube.force-ssl',
        "openid",
    ]

    def __init__(self):
        self._credentials = google_raw_login_get_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        # This is how it's implemented in the official SDK
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()

        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()

        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise ApplicationError("Failed to obtain access token from Google.")

        tokens = response.json()
        print('tokens["id_token"]: ',tokens["id_token"])

        google_tokens = GoogleAccessTokens(
            id_token=tokens["id_token"],
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )

        return google_tokens

    def get_user_info(self, *, google_tokens: GoogleAccessTokens) -> Dict[str, Any]:
        access_token = google_tokens.access_token
        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
        response = requests.get(self.GOOGLE_USER_INFO_URL, params={"access_token": access_token})

        if not response.ok:
            raise ApplicationError("Failed to obtain user info from Google.")

        return response.json()

    def revoke_client_access(self, *, google_tokens: GoogleAccessTokens) -> Dict[str, Any]:
        access_token = google_tokens.access_token
        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
        response = requests.get(
            self.GOOGLE_ACCESS_REVOKE_URL,
            params={"token": access_token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )

        if not response.ok:
            raise ApplicationError("Failed to revoke access.")

        return response.json()

    def refresh_access_token(self, refresh_token: str):
        response = requests.post(
            self.GOOGLE_REFRESH_ACCESS_TOKEN_URL,
            params={
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            },
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )

        if not response.ok:
            raise ApplicationError("Failed to revoke access.")

        return response.json()


def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    project_id = settings.GOOGLE_OAUTH2_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env.")

    credentials = GoogleRawLoginCredentials(client_id=client_id, client_secret=client_secret, project_id=project_id)

    return credentials
