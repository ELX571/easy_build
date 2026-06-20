from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Max
import json

from .models import ChatRoom, Message

User = get_user_model()


def _avatar_url(user, request):
    try:
        if user.profile.avatar:
            return request.build_absolute_uri(user.profile.avatar.url)
    except Exception:
        pass
    return None


# =============================================================================
# SAHIFA VIEW'LARI
# =============================================================================

@login_required
def chat_view(request):
    my_rooms = (
        ChatRoom.objects
        .filter(participants=request.user)
        .prefetch_related('participants', 'messages')
        .order_by('-created_at')
    )

    rooms_data = []
    for room in my_rooms:
        last_msg = room.get_last_message()
        if room.is_group:
            rooms_data.append({
                'room': room,
                'other_user': None,
                'name': room.group_name or f"Jamoa #{room.pk}",
                'is_group': True,
                'last_message': last_msg,
                'unread_count': room.unread_count_for(request.user),
            })
        else:
            other = room.participants.exclude(pk=request.user.pk).first()
            if not other:
                continue
            rooms_data.append({
                'room': room,
                'other_user': other,
                'name': other.get_full_name() or other.username,
                'is_group': False,
                'last_message': last_msg,
                'unread_count': room.unread_count_for(request.user),
            })

    all_users = User.objects.exclude(pk=request.user.pk).order_by('username')

    context = {
        'rooms_data': rooms_data,
        'all_users': all_users,
        'current_user': request.user,
        'me_id': request.user.id,
        'me_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'chat/chat.html', context)


# =============================================================================
# REST API
# =============================================================================

@login_required
@require_GET
def api_contacts(request):
    my_rooms = (
        ChatRoom.objects
        .filter(participants=request.user)
        .prefetch_related('participants', 'messages')
    )

    contacts = []
    for room in my_rooms:
        last_msg = room.get_last_message()
        if room.is_group:
            group_avatar_url = None
            if room.group_avatar:
                group_avatar_url = request.build_absolute_uri(room.group_avatar.url)
            elif room.team_profile and room.team_profile.profile.avatar:
                group_avatar_url = request.build_absolute_uri(room.team_profile.profile.avatar.url)
                
            parts = []
            for p in room.participants.all():
                parts.append({
                    'id': p.pk,
                    'name': p.get_full_name() or p.username,
                    'avatar': _avatar_url(p, request)
                })
                
            contacts.append({
                'room_id': room.pk,
                'user_id': None,
                'name': room.group_name or f"Jamoa #{room.pk}",
                'username': 'team',
                'avatar': group_avatar_url,
                'last_message': last_msg.content if last_msg else '',
                'last_time': last_msg.time_str() if last_msg else '',
                'unread': room.unread_count_for(request.user),
                'online': False,
                'is_group': True,
                'participants': parts
            })
        else:
            other = room.participants.exclude(pk=request.user.pk).first()
            if not other:
                continue
            contacts.append({
                'room_id': room.pk,
                'user_id': other.pk,
                'name': other.get_full_name() or other.username,
                'username': other.username,
                'avatar': _avatar_url(other, request),
                'last_message': last_msg.content if last_msg else '',
                'last_time': last_msg.time_str() if last_msg else '',
                'unread': room.unread_count_for(request.user),
                'online': False,
                'is_group': False
            })

    contacts.sort(key=lambda x: x['last_time'] or '', reverse=True)
    return JsonResponse({'contacts': contacts})


@login_required
@require_GET
def api_messages(request, room_id):
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

    Message.objects.filter(
        room=room, is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    data = [m.to_dict(request) for m in msgs]
    return JsonResponse({'messages': data, 'room_id': room_id})


@login_required
@require_POST
def api_start_chat(request):
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
            'avatar': _avatar_url(other, request),
        }
    })


@login_required
@require_GET
def api_users(request):
    q = request.GET.get('q', '').strip()
    users = User.objects.exclude(pk=request.user.pk).select_related('profile')

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    data = []
    for u in users[:30]:
        data.append({
            'id': u.pk,
            'name': u.get_full_name() or u.username,
            'username': u.username,
            'avatar': _avatar_url(u, request),
            'role': getattr(getattr(u, 'profile', None), 'get_role_display', lambda: '')(),
        })

    return JsonResponse({'users': data})


@login_required
@require_GET
def api_unread_total(request):
    total = 0
    rooms = ChatRoom.objects.filter(participants=request.user)
    for room in rooms:
        total += room.unread_count_for(request.user)
    return JsonResponse({'total_unread': total})

@login_required
@require_POST
def api_update_group(request, room_id):
    room = get_object_or_404(ChatRoom, pk=room_id, is_group=True)
    
    # Check if user is in the group
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
        
    return JsonResponse({
        'success': True, 
        'new_name': room.group_name, 
        'avatar_url': request.build_absolute_uri(room.group_avatar.url) if room.group_avatar else (request.build_absolute_uri(room.team_profile.profile.avatar.url) if room.team_profile and room.team_profile.profile.avatar else None)
    })
