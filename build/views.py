from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from accounts.models import Profile
from accounts.form import ProfileEditForm  # form nomini to'g'ri import qiling
from build.models import Post, BuilderProfile


# =========================================================================
# ASOSIY BOSH SAHIFA: MARKET PRO & SMART FILTER
# =========================================================================
class PostListView(ListView):
    model = Post
    template_name = 'build/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6  # Har sahifada 6 ta post

    def get_queryset(self):
        from django.db.models import Count, Case, When, IntegerField, F
        
        # 1. Asosiy query: e'lonlar va like'larni sanash
        queryset = Post.objects.select_related('author__profile').annotate(
            likes_count=Count('likes', distinct=True)
        )

        # 2. Foydalanuvchi roliga qarab filtrlash (Kross-tavsiya)
        if self.request.user.is_authenticated:
            try:
                user_role = self.request.user.profile.role
                user_city = self.request.user.profile.city
                
                if user_role == 'client':
                    # Oddiy userga faqat ustalar (builder/team) postlari ko'rinadi
                    queryset = queryset.filter(author__profile__role__in=['builder', 'team'])
                elif user_role in ['builder', 'team']:
                    # Ustalarga faqat oddiy userlar (client) postlari ko'rinadi
                    queryset = queryset.filter(author__profile__role='client')
                    
                # 3. Sun'iy Intellekt (AI) Tavsiya Algoritmi (AI Scoring)
                # Score: Boosted (+1000), Bir xil shahar (+500), Har bir like (+10)
                queryset = queryset.annotate(
                    ai_score=Case(When(is_boosted=True, then=1000), default=0, output_field=IntegerField()) +
                             Case(When(author__profile__city=user_city, then=500), default=0, output_field=IntegerField()) +
                             (F('likes_count') * 10)
                ).order_by('-ai_score', '-created_time')
                
            except Exception:
                # Profil yo'q bo'lsa default tartib
                queryset = queryset.order_by('-is_boosted', '-created_time')
        else:
            # Mehmonlar uchun barcha postlar AI score'siz
            queryset = queryset.order_by('-is_boosted', '-created_time')

        # 4. Foydalanuvchi qidiruv (qolda filtrlash)
        category = self.request.GET.get('category')
        city = self.request.GET.get('city')

        if category:
            queryset = queryset.filter(category=category)
        if city:
            queryset = queryset.filter(author__profile__city=city)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ustalar ro'yxati (Smart Filter uchun)
        builders = BuilderProfile.objects.filter(is_available=True)

        # Ustalar uchun ham filter
        profession_query = self.request.GET.get('profession')
        city_query = self.request.GET.get('city')

        if profession_query:
            builders = builders.filter(profession__icontains=profession_query)
        if city_query:
            builders = builders.filter(profile__city=city_query)

        context['builders'] = builders
        context['current_city'] = city_query or ''
        return context


# =========================================================================
# FOYDALANUVCHI PROFILLI (DASHBOARD)
# =========================================================================
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    # Profil mavjudligini tekshirish
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'build/profile.html', {'profile': profile})


def profile_edit_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
            return redirect('build:profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'build/profile_edit.html', {'form': form, 'profile': profile})


# build/views.py fayliga qo'shing:
from django.contrib.auth.decorators import login_required
from .form import PostCreateForm


@login_required
def post_create_view(request):

    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Post modelidagi bog'liqlikka qarab
            post.username = request.user.username  # Agar username maydoni CharField bo'lsa
            post.save()
            messages.success(request, "Eʼloningiz muvaffaqiyatli joylashtirildi!")
            return redirect('build:post_list')
    else:
        form = PostCreateForm()

    return render(request, 'build/post_create.html', {'form': form})



from django.db.models import Count, Exists, OuterRef, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PostLike, PostBookmark
import json

def builder_list_view(request):
    builders = BuilderProfile.objects.filter(is_available=True)
    profession = request.GET.get('profession')
    city = request.GET.get('city')
    
    if profession:
        builders = builders.filter(profession__icontains=profession)
    if city:
        builders = builders.filter(profile__city=city)
        
    from django.db.models import Case, When, IntegerField, F
    
    posts = Post.objects.select_related('author__profile').annotate(
        likes_count=Count('likes', distinct=True)
    )
    if request.user.is_authenticated:
        try:
            user_role = request.user.profile.role
            user_city = request.user.profile.city
            
            # Kross-tavsiya filtri
            if user_role == 'client':
                posts = posts.filter(author__profile__role__in=['builder', 'team'])
            elif user_role in ['builder', 'team']:
                posts = posts.filter(author__profile__role='client')
                
            # AI Scoring tizimi
            posts = posts.annotate(
                is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), user=request.user)),
                is_bookmarked=Exists(PostBookmark.objects.filter(post=OuterRef('pk'), user=request.user)),
                ai_score=Case(When(is_boosted=True, then=1000), default=0, output_field=IntegerField()) +
                         Case(When(author__profile__city=user_city, then=500), default=0, output_field=IntegerField()) +
                         (F('likes_count') * 10)
            ).order_by('-ai_score', '-created_time')
        except Exception:
            posts = posts.annotate(
                is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), user=request.user)),
                is_bookmarked=Exists(PostBookmark.objects.filter(post=OuterRef('pk'), user=request.user))
            ).order_by('-is_boosted', '-created_time')
    else:
        posts = posts.order_by('-is_boosted', '-created_time')

    context = {
        'builders': builders,
        'posts': posts,
        'profession': profession,
        'city': city,
        'region_choices': Profile.REGION_CHOICES,
    }
    return render(request, 'build/builder_list.html', context)

class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data
        try:
            post = Post.objects.create(
                author=request.user,
                title=data.get('title', 'Qurilish e\'loni'),
                category=data.get('category', 'material'),
                description=data.get('description', ''),
                price=data.get('price') if data.get('price') else None,
            )
            if 'image' in request.FILES:
                post.image = request.FILES['image']
                post.save()
            return Response({'success': True, 'post_id': post.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TogglePostLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = PostLike.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True
            
        likes_count = post.likes.count()
        return Response({'is_liked': is_liked, 'likes_count': likes_count})

class TogglePostBookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        bookmark, created = PostBookmark.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
            
        return Response({'is_bookmarked': is_bookmarked})

class UserContactInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        from django.contrib.auth.models import User as DjangoUser
        user = get_object_or_404(DjangoUser, id=user_id)
        
        if user == request.user:
            return Response({'error': "O'zingizning ma'lumotlaringiz."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile = user.profile
            avatar_url = request.build_absolute_uri(profile.get_avatar_url())
            telegram = profile.telegram or ''
            if telegram and not telegram.startswith('@') and not telegram.startswith('t.me'):
                telegram = '@' + telegram
            whatsapp = profile.whatsapp or ''
            whatsapp_clean = ''.join(filter(str.isdigit, whatsapp))
            
            return Response({
                'id': user.id,
                'full_name': user.get_full_name() or user.username,
                'username': user.username,
                'avatar': avatar_url,
                'phone': profile.phone or '',
                'telegram': telegram,
                'telegram_url': f"https://t.me/{telegram.lstrip('@')}" if telegram else '',
                'whatsapp': whatsapp,
                'whatsapp_url': f"https://wa.me/{whatsapp_clean}" if whatsapp_clean else '',
                'role': profile.get_role_display(),
                'city': profile.get_city_display() if profile.city else '',
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth.models import User as DjangoUser
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return Response([])

        users = DjangoUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__phone__icontains=query)
        ).exclude(id=request.user.id).order_by('-id')[:20]

        results = []
        for u in users:
            avatar = None
            role_display = ''
            if hasattr(u, 'profile'):
                avatar = request.build_absolute_uri(u.profile.get_avatar_url())
                role_display = u.profile.get_role_display()
            
            results.append({
                'id': u.id,
                'username': u.username,
                'full_name': u.get_full_name() or u.username,
                'avatar': avatar,
                'role': role_display
            })
        return Response(results)

class AddTeamMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from django.contrib.auth.models import User as DjangoUser
        from build.models import TeamInvitation, BuilderProfile
        from chat.models import ChatRoom, Message
        
        try:
            builder_profile = request.user.profile.builder_info
        except Exception:
            if request.user.profile.role == 'team':
                builder_profile = BuilderProfile.objects.create(
                    profile=request.user.profile,
                    profession='Kompaniya/Jamoa',
                    experience_years=0
                )
            else:
                return Response({'error': 'Siz qurilish jamoasi emassiz!'}, status=403)
                
        if request.user.profile.role != 'team':
            return Response({'error': 'Siz qurilish jamoasi emassiz!'}, status=403)
            
        target_user = get_object_or_404(DjangoUser, id=user_id)
        if target_user == request.user:
            return Response({'error': 'O\'zingizni qo\'sha olmaysiz!'}, status=400)
            
        if builder_profile.members.filter(id=target_user.id).exists():
            return Response({'error': 'Foydalanuvchi allaqachon jamoangizda!'}, status=400)
            
        if target_user.joined_teams.count() >= 2:
            return Response({'error': 'Foydalanuvchi eng ko\'pi bilan 2 ta jamoaga a\'zo bo\'lishi mumkin!'}, status=400)
            
        invite, created = TeamInvitation.objects.get_or_create(
            team=builder_profile,
            user=target_user,
            defaults={'status': 'pending'}
        )
        
        if not created and invite.status == 'pending':
            return Response({'error': 'Taklif allaqachon yuborilgan!'}, status=400)
            
        invite.status = 'pending'
        invite.save()
        
        room, _ = ChatRoom.get_or_create_for(request.user, target_user)
        Message.objects.create(room=room, sender=request.user, content=f"__TEAM_INVITE__:{invite.id}")
        return Response({'success': True, 'message': 'Taklif foydalanuvchi chatiga yuborildi!'})

class RemoveTeamMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from django.contrib.auth.models import User as DjangoUser
        try:
            builder_profile = request.user.profile.builder_info
        except Exception:
            return Response({'error': 'Siz qurilish jamoasi emassiz!'}, status=403)
                
        if request.user.profile.role != 'team':
            return Response({'error': 'Siz qurilish jamoasi emassiz!'}, status=403)
            
        target_user = get_object_or_404(DjangoUser, id=user_id)
        builder_profile.members.remove(target_user)
        
        try:
            from chat.models import ChatRoom
            group_room = ChatRoom.objects.get(team_profile=builder_profile)
            group_room.participants.remove(target_user)
        except Exception:
            pass
            
        return Response({'success': True, 'message': 'Foydalanuvchi jamoadan o\'chirildi!'})

class RespondTeamInviteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id):
        from build.models import TeamInvitation
        from chat.models import ChatRoom, Message
        
        invite = get_object_or_404(TeamInvitation, id=invite_id)
        if invite.user != request.user:
            return Response({'error': 'Sizga tegishli taklif emas!'}, status=403)
            
        action = request.data.get('action')
        if action == 'accept':
            if invite.status != 'pending':
                return Response({'error': 'Bu taklifga allaqachon javob berilgan!'}, status=400)
            if request.user.joined_teams.count() >= 2:
                return Response({'error': 'Siz eng ko\'pi bilan 2 ta jamoaga a\'zo bo\'lishingiz mumkin!'}, status=400)
                
            invite.status = 'accepted'
            invite.save()
            invite.team.members.add(request.user)
            
            room, _ = ChatRoom.get_or_create_for(request.user, invite.team.profile.user)
            Message.objects.create(room=room, sender=request.user, content=f"🤝 Men jamoangizga qo'shilish taklifini qabul qildim!")
            
            team_owner_name = invite.team.profile.user.get_full_name() or invite.team.profile.user.username
            group_room, created = ChatRoom.objects.get_or_create(
                team_profile=invite.team,
                defaults={'is_group': True, 'group_name': f"🚀 {team_owner_name} Jamoasi"}
            )
            if created:
                group_room.participants.add(invite.team.profile.user)
            group_room.participants.add(request.user)
            
            Message.objects.filter(content=f"__TEAM_INVITE__:{invite.id}").update(content=f"__TEAM_INVITE_ACCEPTED__:{invite.id}")
            return Response({'success': True, 'message': "Jamoaga qo'shildingiz!"})
            
        elif action == 'reject':
            if invite.status != 'pending':
                return Response({'error': 'Bu taklifga allaqachon javob berilgan!'}, status=400)
            invite.status = 'rejected'
            invite.save()
            room, _ = ChatRoom.get_or_create_for(request.user, invite.team.profile.user)
            Message.objects.create(room=room, sender=request.user, content=f"❌ Men jamoangizga qo'shilish taklifini rad etdim.")
            Message.objects.filter(content=f"__TEAM_INVITE__:{invite.id}").update(content=f"__TEAM_INVITE_REJECTED__:{invite.id}")
            return Response({'success': True, 'message': "Taklif rad etildi!"})
            
        return Response({'error': "Noto'g'ri so'rov."}, status=400)

