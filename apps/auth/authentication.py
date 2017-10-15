import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.utils import timezone


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.get_model().objects.get(key=key)
        except self.get_model().DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        # compare time
        current_time = timezone.now()
        if current_time > token.created + datetime.timedelta(seconds=settings.TOKEN_EXPIRATION_SECS):
            token.delete()
            raise AuthenticationFailed('Token has expired. Removed it from backend.')

        return token.user, token