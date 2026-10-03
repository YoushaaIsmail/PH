from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, OuterRef, Subquery
from .models import Message
from .models import *
User = get_user_model()

# chat/views.py (add at the bottom)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
User = get_user_model()

@login_required
def api_user_list(request):
    current_user = request.user

    # Subquery to get the latest message between current_user and each other user
    latest_msg = Message.objects.filter(
        (Q(sender=current_user, recipient=OuterRef('pk')) |
         Q(sender=OuterRef('pk'), recipient=current_user))
    ).order_by('-timestamp')

    users = User.objects.exclude(id=current_user.id).annotate(
        last_message_content=Subquery(latest_msg.values('content')[:1]),
        last_message_timestamp=Subquery(latest_msg.values('timestamp')[:1]),
        last_message_sender=Subquery(latest_msg.values('sender__username')[:1]),
        last_message_is_read=Subquery(latest_msg.values('is_read')[:1]),
    ).order_by('last_message_timestamp')   # 👈 This ensures ordering by most recent message

    data = []
    for user in users:
        unread_count = Message.objects.filter(
            sender=user, recipient=current_user, is_read=False
        ).count()

        data.append({
            'id': user.id,
            'username': user.username,
            'avatar_initial': user.username[0].upper(),
            'is_online': getattr(user, 'is_online', False),
            'last_message_content': user.last_message_content or '',
            'last_message_timestamp': user.last_message_timestamp.isoformat() if user.last_message_timestamp else None,
            'last_message_sender': user.last_message_sender or '',
            'last_message_is_read': user.last_message_is_read or False,
            'unread_count': unread_count,
        })
    return JsonResponse(data, safe=False)
@login_required
@csrf_exempt
def mark_read(request, other_user_id):
    """Mark all messages from other_user to current_user as read"""
    if request.method == 'POST':
        Message.objects.filter(sender_id=other_user_id, recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def user_list(request):
    current_user = request.user
    # Subquery to get the latest message between current_user and each other user
    latest_message_subquery = Message.objects.filter(
        (Q(sender=current_user, recipient=OuterRef('pk')) |
         Q(sender=OuterRef('pk'), recipient=current_user))
    ).order_by('-timestamp').values('content', 'timestamp', 'sender__username', 'is_read')[:1]

    users = User.objects.exclude(id=current_user.id).annotate(
        last_message_content=Subquery(latest_message_subquery.values('content')),
        last_message_timestamp=Subquery(latest_message_subquery.values('timestamp')),
        last_message_sender=Subquery(latest_message_subquery.values('sender__username')),
        last_message_is_read=Subquery(latest_message_subquery.values('is_read')),
    ).order_by('-last_message_timestamp')  # order by most recent message first

    return render(request, 'chat/index.html', {'users': users})

@login_required
def private_chat(request, other_user_id):
    other_user = get_object_or_404(User, id=other_user_id)
    return render(request, 'chat/room.html', {
        'other_user': other_user,
    })

# chat/api_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, OuterRef, Subquery
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_users_list(request):
    """Get list of users with last message and unread count"""
    current_user = request.user
    
    # Subquery for latest message
    latest_msg = Message.objects.filter(
        (Q(sender=current_user, recipient=OuterRef('pk')) |
         Q(sender=OuterRef('pk'), recipient=current_user))
    ).order_by('-timestamp')
    
    users = User.objects.exclude(id=current_user.id).annotate(
        last_message_content=Subquery(latest_msg.values('content')[:1]),
        last_message_timestamp=Subquery(latest_msg.values('timestamp')[:1]),
        last_message_sender=Subquery(latest_msg.values('sender__username')[:1]),
        last_message_is_read=Subquery(latest_msg.values('is_read')[:1]),
    ).order_by('-last_message_timestamp')
    
    data = []
    for user in users:
        unread_count = Message.objects.filter(
            sender=user, recipient=current_user, is_read=False
        ).count()
        
        data.append({
            'id': user.id,
            'username': user.username,
            'photo': user.photo.url if user.photo else None,
            'is_online': getattr(user, 'is_online', False),
            'last_message': {
                'content': user.last_message_content or '',
                'timestamp': user.last_message_timestamp.isoformat() if user.last_message_timestamp else None,
                'sender': user.last_message_sender or '',
                'is_read': user.last_message_is_read or False,
            } if user.last_message_content else None,
            'unread_count': unread_count,
        })
    
    return Response({'data': data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_messages(request, user_id):
    """Get chat history between current user and another user"""
    current_user = request.user
    
    messages = Message.objects.filter(
        (Q(sender=current_user, recipient_id=user_id) |
         Q(sender_id=user_id, recipient=current_user))
    ).select_related('sender', 'recipient').order_by('timestamp')
    
    # Mark messages as read
    Message.objects.filter(sender_id=user_id, recipient=current_user, is_read=False).update(is_read=True)
    
    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'recipient': msg.recipient.username,
            'recipient_id': msg.recipient.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_read': msg.is_read,
        })
    
    return Response({'data': data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Send a new message"""
    current_user = request.user
    recipient_id = request.data.get('recipient_id')
    content = request.data.get('content')
    
    if not recipient_id or not content:
        return Response({'error': 'Missing fields'}, status=400)
    
    recipient = User.objects.get(id=recipient_id)
    
    message = Message.objects.create(
        sender=current_user,
        recipient=recipient,
        content=content,
        is_read=False
    )
    
    return Response({
        'data': {
            'id': message.id,
            'sender': message.sender.username,
            'sender_id': message.sender.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read,
        }
    })