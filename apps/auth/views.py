import requests
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

# Create your views here.
from rest_framework.response import Response
from apps.common.loggers import logger
from apps.common.utils import WXBizDataCrypt
from qr_server.settings import WEIXIN_API_URL, WEIXIN_APP_ID, WEIXIN_SECRET_KEY


class WeixinAuthToken(ObtainAuthToken):

    # accept {'jsCode': xxxx} or {'iv': xxx, 'encryptedData': xxx, 'jsCode': xxxx}
    # The later one will connect weixin openid to ctx if all credential is correct.
    def post(self, request):
        if 'jsCode' not in request.data:
            return Response('No js code', status=status.HTTP_400_BAD_REQUEST)
        open_id, session_key = self._weixin_code_to_openid(request.data['jsCode'])
        if not open_id:
            return Response({'msg': 'Failed to login, Weixin code is wrong'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(username=open_id).first()
        # try to connect ctx and weixin account
        if not user:
            user = get_user_model().objects.create(username=open_id)
        if 'iv' in request.data and 'encryptedData' in request.data:
            try:
                self._update_user_info(user, session_key, request.data['iv'], request.data['encryptedData'])
            except Exception:
                user.weixin_img = request.data.get('avatarUrl')
                user.weixin_nickname = request.data.get('nickName')

        return Response(dict(token=self._get_token(user).key))


    @staticmethod
    def _update_user_info(user, session_key, iv, encrypted_data):
        try:
            pc = WXBizDataCrypt(WEIXIN_APP_ID, session_key)
            data = pc.decrypt(encrypted_data, iv)
            user.weixin_img = data.get('avatarUrl')
            user.weixin_nickname = str(data.get('nickName'))
            user.save()
        except Exception as e:
            logger.error(str(e))
            raise e


    @staticmethod
    def _get_token(in_user):
        token, created = Token.objects.get_or_create(user=in_user)
        token.created = timezone.now()
        token.save()

        return token


    @staticmethod
    def _weixin_code_to_openid(js_code):
        result = (None, None)
        response = requests.get('{0}?appid={1}&secret={2}&js_code={3}&grant_type=authorization_code'.format(
            WEIXIN_API_URL, WEIXIN_APP_ID, WEIXIN_SECRET_KEY, js_code,
        ))
        if response.status_code == status.HTTP_200_OK:
            result = (response.json().get('openid'), response.json().get('session_key'))

        return result

weixin_auth_token = WeixinAuthToken.as_view()
