from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from .models import ChatRoom, Message

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
#  ASOSIY CHAT SAHIFA
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def chat_view(request):
    """
    Chat asosiy sahifasi.
    Barcha xonalar va foydalanuvchilar ro'yxatini kontekstda yuboradi.
    """
    # Joriy foydalanuvchi ishtirokchi bo'lgan xonalar
    my_rooms = (
        ChatRoom.objects
        .filter(participants=request.user)
        .prefetch_related('participants', 'messages')
        .order_by('-created_at')
    )

    # Har bir xona uchun meta ma'lumotlar tayyorlash
    rooms_data = []
    for room in my_rooms:
        other = room.participants.exclude(pk=request.user.pk).first()
        if not other:
            continue
        last_msg = room.get_last_message()
        rooms_data.append({
            'room': room,
            'other_user': other,
            'last_message': last_msg,
            'unread_count': room.unread_count_for(request.user),
        })

    # Yangi suhbat boshlash uchun foydalanuvchilar ro'yxati
    all_users = User.objects.exclude(pk=request.user.pk).order_by('username')

    context = {
        'rooms_data': rooms_data,
        'all_users': all_users,
        'current_user': request.user,
    }
    return render(request, 'chat/chat.html', context)


@login_required
def room_view(request, room_id):
    """Muayyan xona sahifasi (ixtiyoriy — SPA-style chatda ishlatilmaydi)."""
    room = get_object_or_404(ChatRoom, pk=room_id)
    if not room.participants.filter(pk=request.user.pk).exists():
        return redirect('chat:chat')
    return redirect('chat:chat')


# ─────────────────────────────────────────────────────────────────────────────
#  REST API — CONTACTS (Sidebar uchun)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_GET
def api_contacts(request):
    """
    GET /chat/api/contacts/
    Joriy foydalanuvchining barcha suhbat kontaktlarini qaytaradi.
    """
    my_rooms = (
        ChatRoom.objects
        .filter(participants=request.user)
        .prefetch_related('participants', 'messages')
    )

    contacts = []
    for room in my_rooms:
        other = room.participants.exclude(pk=request.user.pk).first()
        if not other:
            continue
        last_msg = room.get_last_message()

        # Avatar
        avatar_url = None
        if hasattr(other, 'profile') and other.profile.avatar:
            avatar_url = request.build_absolute_uri(other.profile.avatar.url)

        contacts.append({
            'room_id': room.pk,
            'user_id': other.pk,
            'name': other.get_full_name() or other.username,
            'username': other.username,
            'avatar': avatar_url,
            'last_message': last_msg.content if last_msg else '',
            'last_time': last_msg.time_str() if last_msg else '',
            'unread': room.unread_count_for(request.user),
            'online': False,  # Keyinchalik presence channel bilan kengaytirish mumkin
        })

    # So'nggi xabarga qarab saralash
    contacts.sort(key=lambda x: x['last_time'] or '', reverse=True)
    return JsonResponse({'contacts': contacts})


# ─────────────────────────────────────────────────────────────────────────────
#  REST API — ROOM MESSAGES
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_GET
def api_messages(request, room_id):
    """
    GET /chat/api/room/<room_id>/messages/
    Berilgan xonaning xabarlar tarixini qaytaradi.
    Pagination: ?offset=0&limit=50
    """
    room = get_object_or_404(ChatRoom, pk=room_id)

    # Ruxsat tekshiruvi
    if not room.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 50))

    msgs = (
        Message.objects
        .filter(room=room)
        .select_related('sender')
        .order_by('created_at')[offset: offset + limit]
    )

    # O'qilmagan xabarlarni o'qildi deb belgilash
    Message.objects.filter(
        room=room, is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    data = []
    for m in msgs:
        avatar_url = None
        if hasattr(m.sender, 'profile') and m.sender.profile.avatar:
            avatar_url = request.build_absolute_uri(m.sender.profile.avatar.url)

        data.append({
            'id': m.pk,
            'sender_id': m.sender.pk,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'sender_avatar': avatar_url,
            'content': m.content,
            'time': m.time_str(),
            'is_read': m.is_read,
        })

    return JsonResponse({'messages': data, 'room_id': room_id})


# ─────────────────────────────────────────────────────────────────────────────
#  REST API — XONA YARATISH / TOPISH
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def api_start_chat(request):
    """
    POST /chat/api/start/
    Body: { "user_id": <int> }
    Yangi xona yaratadi yoki mavjudini qaytaradi.
    """
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
        }
    })


# ─────────────────────────────────────────────────────────────────────────────
#  REST API — FOYDALANUVCHILAR RO'YXATI (Yangi chat uchun)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_GET
def api_users(request):
    """
    GET /chat/api/users/?q=<qidiruv>
    Platformadagi barcha foydalanuvchilarni qaytaradi (o'zidan tashqari).
    """
    q = request.GET.get('q', '').strip()
    users = User.objects.exclude(pk=request.user.pk)

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    data = []
    for u in users[:30]:
        avatar_url = None
        if hasattr(u, 'profile') and u.profile.avatar:
            avatar_url = request.build_absolute_uri(u.profile.avatar.url)
        data.append({
            'id': u.pk,
            'name': u.get_full_name() or u.username,
            'username': u.username,
            'avatar': avatar_url,
        })

    return JsonResponse({'users': data})
