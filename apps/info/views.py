from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from apps.common.common_views import GetContextMixin
from apps.info.models import Message
from apps.info.serializers import MessageSerializer


class MessageViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet,
                     GetContextMixin):
    model = Message
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    #permission_classes = (IsAuthenticated, )
