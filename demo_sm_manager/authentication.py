
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
import jwt
from django.utils.translation import gettext_lazy as _

from django.conf import settings
User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Default Auth class to handle Bearer JWT token received from HTTP_AUTHORIZATION
    """
    def authenticate(self, request):
        self.request = request
        token = self.get_token_from_request('Bearer')
        if not token:
            return None
        return self.authenticate_token(token)
    
    def get_token_from_request(self, start_str):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith(f'{start_str} '):
            return auth_header.split(' ')[1]

        return None

    def authenticate_token(self, token) -> tuple:
        decoded_token = self.decode_jwt_token(token)

        user_id = decoded_token.get('user_id')

        if not user_id:
            raise exceptions.AuthenticationFailed(_('Invalid token'))
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('User not found'))
        return (user, None) 
    
    @staticmethod
    def decode_jwt_token(token: str):
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(_('Token has expired'))
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(_('Invalid token'))