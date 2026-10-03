# PH/asgi.py
import os
import django  # أضف هذا السطر
from django.core.asgi import get_asgi_application

# قم بتهيئة Django قبل أي استيراد محلي
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PH.settings')
django.setup()  # هذا السطر مهم جداً

# الآن يمكن استيراد المكونات التي تستخدم Django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})