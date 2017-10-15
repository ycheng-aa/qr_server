"""qr_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.module_loading import autodiscover_modules
from apps.auth.views import weixin_auth_token
from apps.common.routers import routers


autodiscover_modules('routers')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/weixin_login/$', weixin_auth_token),
    url(r'^api/v1/', include(routers.urls)),
]
