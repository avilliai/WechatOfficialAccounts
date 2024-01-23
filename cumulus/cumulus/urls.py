from django.urls import path
from cumulus.views import weixin_main

urlpatterns = [
    path('wechat', weixin_main)
]