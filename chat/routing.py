# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # مثال: ws/chat/5/ حيث 5 هو معرف المستخدم الآخر
    re_path(r'ws/chat/(?P<other_user_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
]