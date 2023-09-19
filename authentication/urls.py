from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    GoogleLoginApi,
    GoogleLoginRedirectApi,
    CustomTokenRefreshView,
    UpdateUserDetailsApi,
    LogoutView
)


app_name = 'authentication'

google_auth = [
    path("callback/", GoogleLoginApi.as_view(), name="callback-raw"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect"),
    # path("revoke/", GoogleRevokeAccessApi.as_view(), name="revoke"),
]

user_urls = [
    path("update/", UpdateUserDetailsApi.as_view(), name="update"),
]

urlpatterns = [
    path("google-oauth2/", include((google_auth, 'google-oauth2'), namespace="google-oauth2")),
    path("user/", include((user_urls, 'user'), namespace="user")),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]