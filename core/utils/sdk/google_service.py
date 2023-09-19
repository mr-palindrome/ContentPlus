from typing import Any, Dict
import requests

import google_auth_oauthlib.flow
import google.oauth2.credentials
import google.auth.transport.requests
import jwt
import requests
from attrs import define

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.urls import reverse_lazy

from common.utils.exceptions import ApplicationError
from authentication.models import GoogleTokens

@define
class GoogleSdkLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


@define
class GoogleAccessTokens:
    id_token: str
    access_token: str
    refresh_token: str

    def decode_id_token(self) -> Dict[str, Any]:
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token


class GoogleSdkLoginFlowService:
    # API_URI = reverse_lazy("api:google-oauth2:login-sdk:callback-sdk")
    API_URI = reverse_lazy("authentication:google-oauth2:callback-raw")

    # Two options are available: 'web', 'installed'
    GOOGLE_CLIENT_TYPE = "web"

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_ACCESS_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    GOOGLE_REFRESH_ACCESS_TOKEN_URL = "https://oauth2.googleapis.com/token"

    # Add auth_provider_x509_cert_url if you want verification on JWTS such as ID tokens
    GOOGLE_AUTH_PROVIDER_CERT_URL = ""

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
        self._credentials = google_sdk_login_get_credentials()

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    def _generate_client_config(self):
        # This follows the structure of the official "client_secret.json" file
        client_config = {
            self.GOOGLE_CLIENT_TYPE: {
                "client_id": self._credentials.client_id,
                "project_id": self._credentials.project_id,
                "auth_uri": self.GOOGLE_AUTH_URL,
                "token_uri": self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL,
                "auth_provider_x509_cert_url": self.GOOGLE_AUTH_PROVIDER_CERT_URL,
                "client_secret": self._credentials.client_secret,
                "redirect_uris": [self._get_redirect_uri()],
                "javascript_origins": [],
                # "javascript_origins": [settings.BASE_FRONTEND_URL],
            }
        }
        return client_config

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()
        client_config = self._generate_client_config()

        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#creatingclient
        google_oauth_flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_config, scopes=self.SCOPES
        )
        google_oauth_flow.redirect_uri = redirect_uri

        authorization_url, state = google_oauth_flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="select_account",
        )
        return authorization_url, state

    def get_tokens(self, *, code: str, state: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()
        client_config = self._generate_client_config()

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_config, scopes=self.SCOPES, state=state
        )
        flow.redirect_uri = redirect_uri
        try:
            access_credentials_payload = flow.fetch_token(code=code)
        except Exception as e:
            print(e)
            raise ApplicationError(f"Failed to obtain access credentials from Google {e}.") from e

        if not access_credentials_payload:
            raise ValidationError("Failed to obtain access credentials from Google")

        ####
        credentials = flow.credentials
        print(credentials)
        print(dir(credentials))
        creds = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
        print('credentials: ',creds )
        ####
        google_tokens = GoogleAccessTokens(
            id_token=access_credentials_payload["id_token"],
            access_token=access_credentials_payload["access_token"],
            refresh_token=access_credentials_payload["refresh_token"]
        )

        return google_tokens, creds

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

    def refresh_access_token(self, credentials: GoogleTokens) -> google.oauth2.credentials.Credentials:
        credentials = google.oauth2.credentials.Credentials(**{'token': credentials.access_token,
          'refresh_token': credentials.refresh_token,
          'token_uri': self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL,
          'client_id': self._credentials.client_id,
          'client_secret': self._credentials.client_secret,
          'scopes': self.SCOPES})

        credentials.refresh(google.auth.transport.requests.Request())

        return credentials


def google_sdk_login_get_credentials() -> GoogleSdkLoginCredentials:
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    project_id = settings.GOOGLE_OAUTH2_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env.")

    credentials = GoogleSdkLoginCredentials(client_id=client_id, client_secret=client_secret, project_id=project_id)

    return credentials
