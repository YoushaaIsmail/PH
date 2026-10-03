# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None  # تعيين قيمة افتراضية
        self.other_user_id = None
        self.current_user = None
    
    async def connect(self):
        print("🔌 [WebSocket] محاولة اتصال...")
        
        # استخراج token من query string
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get('token', [None])[0]
        
        print(f"🔑 [WebSocket] Token: {token_key[:20] if token_key else 'None'}...")
        
        # التحقق من المستخدم عبر token
        if token_key:
            self.current_user = await self.get_user_from_token(token_key)
        else:
            self.current_user = self.scope.get('user', AnonymousUser())
        
        # إذا كان المستخدم مجهول أو غير مسجل
        if self.current_user is None or self.current_user.is_anonymous:
            print("❌ [WebSocket] مستخدم غير مصرح به، يتم رفض الاتصال")
            await self.close(code=4001)
            return
        
        print(f"✅ [WebSocket] مستخدم مصرح به: {self.current_user.username} (ID: {self.current_user.id})")
        
        # الحصول على معرف المستخدم الآخر من URL
        self.other_user_id = int(self.scope['url_route']['kwargs']['other_user_id'])
        print(f"👥 [WebSocket] المحادثة مع المستخدم ID: {self.other_user_id}")
        
        # إنشاء اسم غرفة فريد بناءً على معرفي المستخدمين
        user_ids = sorted([str(self.current_user.id), str(self.other_user_id)])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'
        print(f"🏠 [WebSocket] اسم الغرفة: {self.room_group_name}")
        
        # الانضمام إلى المجموعة
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print("✅ [WebSocket] تم قبول الاتصال")
        
        # إرسال الرسائل السابقة
        previous_messages = await self.get_previous_messages(self.current_user.id, self.other_user_id)
        for msg_data in previous_messages:
            await self.send(text_data=json.dumps({
                'sender': msg_data['sender_username'],
                'content': msg_data['content'],
                'timestamp': msg_data['timestamp'],
            }))

    async def disconnect(self, close_code):
        print(f"🔌 [WebSocket] قطع الاتصال: {close_code}")
        # التحقق من وجود room_group_name قبل محاولة استخدامه
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        else:
            print("⚠️ [WebSocket] room_group_name غير موجود، تخطي")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        
        print(f"📩 [WebSocket] رسالة واردة: {content}")

        # حفظ الرسالة والحصول على بياناتها المُسلسلة
        message_data = await self.save_message(
            self.current_user.id,
            self.other_user_id,
            content
        )

        # إرسال الرسالة إلى المجموعة
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'private_message',
                'sender': message_data['sender_username'],
                'content': message_data['content'],
                'timestamp': message_data['timestamp'],
            }
        )

    async def private_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'content': event['content'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            print(f"✅ [DB] Token صالح للمستخدم: {token.user.username}")
            return token.user
        except Token.DoesNotExist:
            print(f"❌ [DB] Token غير صالح: {token_key}")
            return None

    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, content):
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=content,
            is_read=False
        )
        print(f"💾 [DB] تم حفظ الرسالة: {sender.username} -> {recipient.username}")
        return {
            'sender_username': sender.username,
            'content': content,
            'timestamp': str(message.timestamp),
        }

    @database_sync_to_async
    def get_previous_messages(self, user1_id, user2_id, limit=50):
        from django.db.models import Q
        messages = Message.objects.filter(
            (Q(sender_id=user1_id) & Q(recipient_id=user2_id)) |
            (Q(sender_id=user2_id) & Q(recipient_id=user1_id))
        ).select_related('sender', 'recipient').order_by('-timestamp')[:limit]
        # نعكس الترتيب ليكون تصاعدياً (من الأقدم إلى الأحدث)
        messages = list(reversed(messages))
        print(f"📜 [DB] تم تحميل {len(messages)} رسالة سابقة")
        return [
            {
                'sender_username': msg.sender.username,
                'content': msg.content,
                'timestamp': str(msg.timestamp),
            }
            for msg in messages
        ]