from apps.common.routers import routers
from apps.info.views import MessageViewSet

routers.register(r'messages', MessageViewSet)
