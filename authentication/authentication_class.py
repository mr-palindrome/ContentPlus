from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
import jwt
from django.conf import settings
from django.utils import timezone
from .models import BaseUser, GoogleTokens  # Import your User model here


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Get the JWT token from the request headers
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            # Extract the token from the "Bearer" prefix
            token = auth_header.split()[1]
            # Decode the JWT token using the secret key
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(payload)
            # Retrieve the user data based on the decoded token
            user_id = payload['user_id']
            user = BaseUser.objects.get(pk=user_id)

            # Check token expiration
            expiration_timestamp = payload.get('exp')
            print(timezone.datetime.utcfromtimestamp(expiration_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
            print(timezone.now())
            request.credentials = GoogleTokens.objects.get(user=user)

            return user, None
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Token is invalid')
        except BaseUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
