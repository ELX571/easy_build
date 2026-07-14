from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Count, Case, When, IntegerField
from django.core.cache import cache
import json

from .models import ChatRoom, Message

User = get_user_model()


def _get_avatar_url(user, request):
    """Helper method to safely fetch user avatar."""
    try:
        return request.build_absolute_uri(user.profile.get_avatar_url())
    except Exception:
        return None


def _format_contact_data(room, user, request, unread_count=None):
    """Formats a single ChatRoom instance into a dictionary for API responses."""
    last_msg = room.get_last_message()
    unread = unread_count if unread_count is not None else room.unread_count_for(user)

    if room.is_group:
        group_avatar_url = None
        if room.group_avatar:
            group_avatar_url = request.build_absolute_uri(room.group_avatar.url)
        elif room.team_profile:
            group_avatar_url = request.build_absolute_uri(room.team_profile.profile.get_avatar_url())

        participants = [
            {
                'id': p.pk,
                'name': p.get_full_name() or p.username,
                'avatar': _get_avatar_url(p, request)
            } for p in room.participants.all()
        ]

        return {
            'room_id': room.pk,
            'user_id': None,
            'name': room.group_name or f"Jamoa #{room.pk}",
            'username': 'team',
            'avatar': group_avatar_url,
            'last_message': last_msg.content if last_msg else '',
            'last_time': last_msg.time_str() if last_msg else '',
            'sort_time': last_msg.created_at.timestamp() if last_msg else 0,
            'unread': unread,
            'online': False,
            'is_group': True,
            'participants': participants
        }

    # Direct Message Room
    other = room.participants.exclude(pk=user.pk).first()
    if not other:
        return None

    payment_info = None
    if other and (other.is_superuser or other.is_staff or user.is_superuser or user.is_staff):
        builder_user = user if (other.is_superuser or other.is_staff) else other
        if hasattr(builder_user, 'profile') and builder_user.profile.role == 'builder':
            bp = getattr(builder_user.profile, 'builder_info', None)
            if bp:
                from build.models import SubscriptionRequest
                latest_req = SubscriptionRequest.objects.filter(user=builder_user).order_by('-created_at').first()
                payment_info = {
                    'pending_plan': bp.pending_plan.name if bp.pending_plan else None,
                    'pending_price': str(bp.pending_plan.price) if bp.pending_plan else None,
                    'is_temp_active': bp.is_temp_active,
                    'subscription_status': bp.subscription_status,
                    'subscription_plan': bp.subscription_plan.name if bp.subscription_plan else None,
                    'request_status': latest_req.status if latest_req else None,
                    'request_id': latest_req.id if latest_req else None,
                }

    return {
        'room_id': room.pk,
        'user_id': other.pk,
        'name': other.get_full_name() or other.username,
        'username': other.username,
        'avatar': _get_avatar_url(other, request),
        'last_message': last_msg.content if last_msg else '',
        'last_time': last_msg.time_str() if last_msg else '',
        'sort_time': last_msg.created_at.timestamp() if last_msg else 0,
        'unread': unread,
        'online': bool(cache.get(f'user_online_{other.pk}')),
        'is_group': False,
        'payment_info': payment_info
    }


# =============================================================================
# HTML VIEWS
# =============================================================================

@login_required
def chat_view(request):
    """Renders the main chat application page."""
    # Active subscription check for builders
    if hasattr(request.user, 'profile') and request.user.profile.role == 'builder':
        bp = getattr(request.user.profile, 'builder_info', None)
        if not bp or not bp.has_active_subscription:
            from django.utils.translation import get_language
            from django.shortcuts import redirect
            return redirect(f"/{get_language()}/payment-dashboard/")

    my_rooms = (
        ChatRoom.objects
        .filter(participants=request.user)
        .prefetch_related('participants')
        .order_by('-created_at')
    )

    rooms_data = []
    for room in my_rooms:
        data = _format_contact_data(room, request.user, request)
        if data:
            # chat_view expects a slightly different structure for rendering
            data['room'] = room
            data['other_user'] = room.participants.exclude(pk=request.user.pk).first() if not room.is_group else None
            data['unread_count'] = data['unread']
            rooms_data.append(data)

    all_users = User.objects.exclude(pk=request.user.pk).select_related('profile').order_by('username')

    context = {
        'rooms_data': rooms_data,
        'all_users': all_users,
        'current_user': request.user,
        'me_id': request.user.id,
        'me_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'chat/chat.html', context)


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@login_required
@require_GET
def api_contacts(request):
    """Returns a list of all active chat rooms/contacts for the current user."""
    # Annotating unread count to prevent N+1 query issue
    my_rooms = (
        ChatRoom.objects
        .filter(participants=request.user)
        .annotate(
            unread_count=Count(
                Case(
                    When(messages__is_read=False, messages__sender__isnull=False, then=1),
                    output_field=IntegerField()
                ),
                filter=~Q(messages__sender=request.user)
            )
        )
        .prefetch_related('participants__profile')
    )

    contacts = []
    for room in my_rooms:
        data = _format_contact_data(room, request.user, request, unread_count=room.unread_count)
        if data:
            contacts.append(data)

    # Sort contacts by the time of the last message
    contacts.sort(key=lambda x: x['sort_time'], reverse=True)
    return JsonResponse({'contacts': contacts})


@login_required
@require_GET
def api_messages(request, room_id):
    """Fetches messages for a specific room and marks unread ones as read."""
    room = get_object_or_404(ChatRoom, pk=room_id)

    if not room.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)

    offset = max(0, int(request.GET.get('offset', 0)))
    limit = min(100, int(request.GET.get('limit', 50)))

    msgs = (
        Message.objects
        .filter(room=room)
        .select_related('sender', 'sender__profile')
        .order_by('created_at')[offset: offset + limit]
    )

    # Mark unread messages sent by others as read
    updated = Message.objects.filter(
        room=room, is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    if updated > 0:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room.pk}',
            {
                'type': 'messages_read',
                'reader_id': request.user.pk,
                'room_id': room.pk,
            }
        )

    data = [m.to_dict(request) for m in msgs]
    return JsonResponse({'messages': data, 'room_id': room_id})


@login_required
@require_POST
def api_start_chat(request):
    """Initiates a new direct chat room with another user."""
    # Active subscription check for builders
    if hasattr(request.user, 'profile') and request.user.profile.role == 'builder':
        bp = getattr(request.user.profile, 'builder_info', None)
        if not bp or not bp.has_active_subscription:
            from django.utils.translation import get_language
            from django.utils.translation import gettext as _
            return JsonResponse({
                'error': _("Bu funksiyadan foydalanish uchun faol obuna talab qilinadi."),
                'redirect': f"/{get_language()}/payment-dashboard/"
            }, status=402)

    try:
        body = json.loads(request.body)
        other_id = int(body.get('user_id', 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Noto\'g\'ri so\'rov'}, status=400)

    if other_id == request.user.pk:
        return JsonResponse({'error': 'O\'zingiz bilan chat boshlash mumkin emas'}, status=400)

    other = get_object_or_404(User, pk=other_id)
    room, created = ChatRoom.get_or_create_for(request.user, other)

    return JsonResponse({
        'room_id': room.pk,
        'created': created,
        'other_user': {
            'id': other.pk,
            'name': other.get_full_name() or other.username,
            'username': other.username,
            'avatar': _get_avatar_url(other, request),
        }
    })


@login_required
@require_GET
def api_users(request):
    """Searches for users by username or name to start a new chat."""
    q = request.GET.get('q', '').strip()
    if q.startswith('@'):
        q = q[1:]
        
    users = User.objects.exclude(pk=request.user.pk).select_related('profile')

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    data = [
        {
            'id': u.pk,
            'name': u.get_full_name() or u.username,
            'username': u.username,
            'avatar': _get_avatar_url(u, request),
            'role': getattr(getattr(u, 'profile', None), 'get_role_display', lambda: '')(),
        } for u in users[:30]
    ]

    return JsonResponse({'users': data})


@login_required
@require_GET
def api_unread_total(request):
    """Calculates the total number of unread messages across all rooms."""
    total = sum(room.unread_count_for(request.user) for room in ChatRoom.objects.filter(participants=request.user))
    return JsonResponse({'total_unread': total})


@login_required
@require_POST
def api_update_group(request, room_id):
    """Updates group room details (name, avatar)."""
    room = get_object_or_404(ChatRoom, pk=room_id, is_group=True)
    
    if not room.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
        
    new_name = request.POST.get('name', '').strip()
    avatar_file = request.FILES.get('avatar')
    updated = False
    
    if new_name:
        room.group_name = new_name
        updated = True
        
    if avatar_file:
        room.group_avatar = avatar_file
        updated = True
        
    if updated:
        room.save()
        
    avatar_url = request.build_absolute_uri(room.group_avatar.url) if room.group_avatar else \
                 (request.build_absolute_uri(room.team_profile.profile.get_avatar_url()) if room.team_profile else None)

    return JsonResponse({
        'success': True, 
        'new_name': room.group_name, 
        'avatar_url': avatar_url
    })


@login_required
@require_POST
def api_upload_file(request, room_id):
    """Handles file uploads and broadcasts the new message via WebSocket."""
    room = get_object_or_404(ChatRoom, pk=room_id)
    if not room.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Forbidden'}, status=403)
        
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
        
    file_type = request.POST.get('file_type', 'document')
    content = request.POST.get('content', '')
    
    message = Message.objects.create(
        room=room,
        sender=request.user,
        content=content,
        file=file,
        file_type=file_type
    )

    # Check if this is a payment verification screenshot upload
    if file_type == 'image' and hasattr(request.user, 'profile') and request.user.profile.role == 'builder':
        other_user = room.participants.exclude(pk=request.user.pk).first()
        if other_user and (other_user.is_superuser or other_user.is_staff):
            bp = getattr(request.user.profile, 'builder_info', None)
            if bp and bp.pending_plan:
                from build.models import SubscriptionRequest
                from django.utils import timezone
                
                # Create SubscriptionRequest
                sub_request = SubscriptionRequest.objects.create(
                    user=request.user,
                    plan_name=bp.pending_plan.name,
                    amount=bp.pending_plan.price,
                    screenshot=file,
                    status='pending'
                )
                
                # Grant 24h temporary access
                bp.is_temp_active = True
                bp.temp_active_until = timezone.now() + timezone.timedelta(hours=24)
                bp.save()
                
                # Create and broadcast system notification message
                sys_content = f"Tizim: To'lov cheki qabul qilindi. {bp.pending_plan.name} tarifi uchun 24 soatlik vaqtinchalik kirish imkoni berildi. Admin tekshiruvi kutilmoqda."
                sys_message = Message.objects.create(
                    room=room,
                    sender=other_user,
                    content=sys_content
                )
                
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'chat_{room.pk}',
                    {
                        'type': 'chat_message',
                        'message_id': sys_message.id,
                        'message': sys_message.content,
                        'sender_id': other_user.id,
                        'sender_name': other_user.get_full_name() or other_user.username,
                        'sender_avatar': _get_avatar_url(other_user, request),
                        'time': sys_message.time_str(),
                        'is_read': False,
                        'room_id': room.pk,
                    }
                )
    
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{room.pk}',
        {
            'type': 'chat_message',
            'message_id': message.id,
            'message': message.content,
            'sender_id': request.user.id,
            'sender_name': request.user.get_full_name() or request.user.username,
            'sender_avatar': _get_avatar_url(request.user, request),
            'time': message.time_str(),
            'is_read': False,
            'file_url': request.build_absolute_uri(message.file.url) if message.file else None,
            'file_type': message.file_type,
            'room_id': room.pk,
        }
    )
    
    return JsonResponse({'success': True, 'message_id': message.id})
