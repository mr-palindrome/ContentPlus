from django.urls import path, include

from .views import (
    GoogleLoginApi,
    GoogleLoginRedirectApi,
    GoogleLoginState,
)


app_name = 'authentication'

google_auth = [
    path("callback/", GoogleLoginApi.as_view(), name="callback-raw"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect-raw"),
    path("state/", GoogleLoginState.as_view(), name="state-raw"),
]

urlpatterns = [
    path("google-oauth2/", include((google_auth, 'google-oauth2'), namespace="google-oauth2")),
    # ... other URL patterns ...
]