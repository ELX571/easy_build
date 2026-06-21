from chat.models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        # User is part of rooms, but we only count messages where they are the recipient and is_read=False
        # A simpler way is to count all unread messages in rooms where the user is a participant but not the sender.
        count = Message.objects.filter(
            room__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_chat_count': count}
    return {'unread_chat_count': 0}
