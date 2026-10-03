# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
     path('', views.user_list, name='user_list'),
    path('api/users/', views.api_user_list, name='api_user_list'),
    path('mark-read/<int:other_user_id>/', views.mark_read, name='mark_read'),
    path('chat/<int:other_user_id>/', views.private_chat, name='private_chat'),
        path('api/chat/users/', views.chat_users_list, name='api_chat_users'),
    path('api/chat/messages/<int:user_id>/', views.chat_messages, name='api_chat_messages'),
    path('api/chat/send/', views.send_message, name='api_chat_send'),
]