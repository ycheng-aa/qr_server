from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.common.serializers import AuthedSerializer
from apps.info.models import Message


class MessageSerializer(AuthedSerializer):
    receiver = serializers.SlugRelatedField(slug_field='username', queryset=get_user_model().objects.all())
    sender = serializers.SlugRelatedField(slug_field='username', queryset=get_user_model().objects.all())

    receiver_nick = serializers.CharField(source='receiver.weixin_nickname', required=False, read_only=True)
    sender_nick = serializers.CharField(source='sender.weixin_nickname', required=False, read_only=True)

    receiver_img = serializers.CharField(source='receiver.weixin_img', required=False, read_only=True)
    sender_img = serializers.CharField(source='sender.weixin_img', required=False, read_only=True)

    info = serializers.CharField(required=True)

    qrcode = serializers.CharField(source='qrcode.url', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'receiver', 'sender', 'info', 'receiver_nick', 'sender_nick',
                  'receiver_img', 'sender_img', 'qrcode')

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.generate_qr_code()

        return instance
