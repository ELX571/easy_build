from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Case, When, IntegerField, F, Exists, OuterRef, Q
from django.utils.translation import gettext as _
from django.utils.translation import get_language  # <-- Dinamik filter uchun tilni aniqlash

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from accounts.models import Profile
from accounts.form import ProfileEditForm
from build.models import Post, BuilderProfile, PostLike, PostBookmark, TeamInvitation, ProjectOrder, ProjectBid
from chat.models import ChatRoom, Message
from .form import PostCreateForm


# =========================================================================
# ASOSIY BOSH SAHIFA: FEED
# =========================================================================
class HomeView(ListView):
    model = Post
    template_name = 'build/home.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        from django.db.models import Q
        q = self.request.GET.get('q')
        qs = Post.objects.select_related('author__profile').annotate(
            likes_count=Count('likes', distinct=True)
        )

        # ── ROLE-BASED FEED FILTER ──
        if self.request.user.is_authenticated:
            try:
                user_role = self.request.user.profile.role
                if user_role == 'client':
                    qs = qs.filter(author__profile__role__in=['builder', 'team'])
                elif user_role in ['builder', 'team']:
                    qs = qs.filter(author__profile__role='client')
            except Exception:
                pass

            # ⭐ Premium ustalar postlari feed tepasida — AI Score bilan birga
            try:
                user_city = self.request.user.profile.city
                qs = qs.annotate(
                    premium_score=Case(
                        When(author__profile__is_premium=True, then=500),
                        default=0,
                        output_field=IntegerField()
                    ),
                    city_score=Case(
                        When(author__profile__city=user_city, then=200),
                        default=0,
                        output_field=IntegerField()
                    )
                )
            except Exception:
                pass

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.order_by('-created_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            liked_ids = set(self.request.user.liked_posts.values_list('post_id', flat=True))
            bookmarked_ids = set(self.request.user.bookmarked_posts.values_list('post_id', flat=True))
            for post in context['posts']:
                post.is_liked = post.id in liked_ids
                post.is_bookmarked = post.id in bookmarked_ids

            from chat.models import Message
            unread_count = Message.objects.filter(
                room__participants=self.request.user,
                is_read=False
            ).exclude(sender=self.request.user).count()
            context['unread_chat_count'] = unread_count

            # Rol context ga uzatiladi (sidebar va feed uchun)
            try:
                context['user_role'] = self.request.user.profile.role
            except Exception:
                context['user_role'] = None
        return context

# =========================================================================
# ASOSIY BOSH SAHIFA: MARKET PRO & SMART FILTER
# =========================================================================
class NetworkView(ListView):
    model = Post
    template_name = 'build/network.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        from django.db.models import Q
        q = self.request.GET.get('q')
        qs = Post.objects.select_related('author__profile').annotate(
            likes_count=Count('likes', distinct=True)
        )

        if self.request.user.is_authenticated:
            try:
                user_role = self.request.user.profile.role
                if user_role in ['builder', 'team']:
                    qs = qs.filter(author__profile__role__in=['builder', 'team'])
                else:
                    qs = qs.filter(author__profile__role='client')
            except Exception:
                pass

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.order_by('-created_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            liked_ids = set(self.request.user.liked_posts.values_list('post_id', flat=True))
            bookmarked_ids = set(self.request.user.bookmarked_posts.values_list('post_id', flat=True))
            for post in context['posts']:
                post.is_liked = post.id in liked_ids
                post.is_bookmarked = post.id in bookmarked_ids

            from chat.models import Message
            unread_count = Message.objects.filter(
                room__participants=self.request.user,
                is_read=False
            ).exclude(sender=self.request.user).count()
            context['unread_chat_count'] = unread_count

            try:
                context['user_role'] = self.request.user.profile.role
            except Exception:
                context['user_role'] = None
        return context

# =========================================================================
# ASOSIY BOSH SAHIFA: MARKET PRO & SMART FILTER
# =========================================================================
class PostListView(ListView):
    model = Post
    template_name = 'build/post_list.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        queryset = Post.objects.select_related('author__profile').annotate(
            likes_count=Count('likes', distinct=True)
        )

        if self.request.user.is_authenticated:
            try:
                user_city = self.request.user.profile.city
                queryset = queryset.annotate(
                    is_liked=Exists(PostLike.objects.filter(post=OuterRef('pk'), user=self.request.user)),
                    is_bookmarked=Exists(PostBookmark.objects.filter(post=OuterRef('pk'), user=self.request.user)),
                    ai_score=Case(When(is_boosted=True, then=1000), default=0, output_field=IntegerField()) +
                             Case(When(author__profile__city=user_city, then=500), default=0,
                                  output_field=IntegerField()) +
                             (F('likes_count') * 10)
                )
            except Exception:
                pass

        category = self.request.GET.get('category')
        if category:
            if category == 'tech':
                queryset = queryset.filter(category__in=['tech', 'equipment'])
            else:
                queryset = queryset.filter(category=category)

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        order_by = self.request.GET.get('order_by')
        if order_by == 'newest':
            queryset = queryset.order_by('-created_time')
        elif order_by == 'oldest':
            queryset = queryset.order_by('created_time')
        elif order_by == 'price_asc':
            queryset = queryset.order_by(F('price').asc(nulls_last=True))
        elif order_by == 'price_desc':
            queryset = queryset.order_by(F('price').desc(nulls_last=True))
        else:
            if self.request.user.is_authenticated:
                queryset = queryset.order_by('-ai_score', '-created_time')
            else:
                queryset = queryset.order_by('-is_boosted', '-created_time')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        builders = BuilderProfile.objects.filter(is_available=True)

        profession_query = self.request.GET.get('profession')
        city_query = self.request.GET.get('city')

        if profession_query:
            builders = builders.filter(profession__icontains=profession_query)
        if city_query:
            builders = builders.filter(profile__city=city_query)

        context['builders'] = builders
        context['current_city'] = city_query or ''
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['current_order'] = self.request.GET.get('order_by', '')
        return context


# =========================================================================
# FOYDALANUVCHI PROFILLI (DASHBOARD)
# =========================================================================
@login_required
def profile_view(request, user_id=None):
    from django.contrib.auth.models import User as DjangoUser
    if user_id:
        target_user = get_object_or_404(DjangoUser, id=user_id)
        profile = get_object_or_404(Profile, user=target_user)
        is_own_profile = False
    else:
        target_user = request.user
        profile, created = Profile.objects.get_or_create(user=target_user)
        is_own_profile = True

    is_liked_subquery = Exists(PostLike.objects.filter(post=OuterRef('pk'), user=request.user))
    is_bookmarked_subquery = Exists(PostBookmark.objects.filter(post=OuterRef('pk'), user=request.user))

    my_posts = Post.objects.filter(author=target_user).select_related('author__profile').annotate(
        likes_count=Count('likes', distinct=True),
        is_liked=is_liked_subquery,
        is_bookmarked=is_bookmarked_subquery
    ).order_by('-created_time')

    liked_post_ids = PostLike.objects.filter(user=target_user).values_list('post_id', flat=True)
    liked_posts = Post.objects.filter(id__in=liked_post_ids).select_related('author__profile').annotate(
        likes_count=Count('likes', distinct=True),
        is_liked=is_liked_subquery,
        is_bookmarked=is_bookmarked_subquery
    ).order_by('-created_time')

    bookmarked_post_ids = PostBookmark.objects.filter(user=target_user).values_list('post_id', flat=True)
    bookmarked_posts = Post.objects.filter(id__in=bookmarked_post_ids).select_related('author__profile').annotate(
        likes_count=Count('likes', distinct=True),
        is_liked=is_liked_subquery,
        is_bookmarked=is_bookmarked_subquery
    ).order_by('-created_time')

    context = {
        'profile': profile,
        'target_user': target_user,
        'is_own_profile': is_own_profile,
        'my_posts': my_posts,
        'liked_posts': liked_posts,
        'bookmarked_posts': bookmarked_posts,
    }
    return render(request, 'build/profile.html', context)


@login_required
def profile_edit_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profilingiz muvaffaqiyatli yangilandi!"))
            return redirect('build:profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'build/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if hasattr(post, 'username'):
                post.username = request.user.username

            post.save()
            form.save_m2m()

            print("\n" + "🔥" * 20)
            print(f"E'LON BAZAGA YOZILDI! ID: {post.id} | Sarlavha: {post.title}")
            print("🔥" * 20 + "\n")

            messages.success(request, _("Eʼloningiz muvaffaqiyatli joylashtirildi!"))
            return redirect('build:profile')
        else:
            print("Forma xatoliklari:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = PostCreateForm()

    return render(request, 'build/post_create.html', {'form': form})


def builder_list_view(request):
    # ⭐ Premium ustalar qidiruv natijalarida BIRINCHI chiqadi
    builders = BuilderProfile.objects.filter(is_available=True).annotate(
        premium_boost=Case(
            When(profile__is_premium=True, then=1000),
            default=0,
            output_field=IntegerField()
        )
    ).order_by('-premium_boost', '-rating_cache')

    # ⚡️ URL dan kelayotgan qiymatlarni o'qib olamiz
    profession = request.GET.get('profession', '').strip()
    city = request.GET.get('city', '').strip()
    current_lang = get_language()

    # ⚡️ Kasblar tarjimasi lug'ati
    profession_mapping = {
        'ru': {
            'Электрик': 'Elektrik', 'Сантехник': 'Santexnik', 'Бетонщик / Арматурщик': 'Betonchi / Armaturachi',
            'Штукатур / Маляр': 'Suvoqchi / Malyar', 'Плиточник': 'Kafelchi (Plitkach)',
            'Сварщик': 'Payvandchi (Svarshik)',
            'Кровельщик': 'Tom yopuvchi (Tomchi)', 'Каменщик': 'G\'isht quyuvchi (G\'ishtchi)',
            'Плотник': 'Duradgor / Yog\'och ustasi',
            'Гипсокартонщик': 'Gipsokartonchi', 'Отопление и охлаждение (HVAC)': 'Isitish va Sovutish (HVAC)',
            'Инженер проекта (Прораб)': 'Loyiha muhandisi (Prorab)', 'Мастер фасада': 'Fasad ustasi',
            'Демонтаж / Снос': 'Demontaj / Buzish ishlari', 'Общий строитель': 'Umumiy quruvchi'
        },
        'en': {
            'Electrician': 'Elektrik', 'Plumber': 'Santexnik', 'Concrete worker / Reinforcer': 'Betonchi / Armaturachi',
            'Plasterer / Painter': 'Suvoqchi / Malyar', 'Tiler': 'Kafelchi (Plitkach)',
            'Welder': 'Payvandchi (Svarshik)',
            'Roofer': 'Tom yopuvchi (Tomchi)', 'Bricklayer': 'G\'isht quyuvchi (G\'ishtchi)',
            'Carpenter': 'Duradgor / Yog\'och ustasi',
            'Drywaller': 'Gipsokartonchi', 'Heating and Cooling (HVAC)': 'Isitish va Sovutish (HVAC)',
            'Project Engineer (Prorab)': 'Loyiha muhandisi (Prorab)', 'Facade Master': 'Fasad ustasi',
            'Demolition / Dismantling': 'Demontaj / Buzish ishlari', 'General Builder': 'Umumiy quruvchi'
        }
    }

    # ⚡️ Shaharlar tarjimasi lug'ati
    city_mapping = {
        'ru': {
            'Город Ташкент': 'Toshkent shahri', 'Ташкентская область': 'Toshkent viloyati',
            'Андижанская область': 'Andijon viloyati', 'Бухарская область': 'Buxoro viloyati',
            'Ферганская область': 'Farg\'ona viloyati', 'Джизакская область': 'Jizzax viloyati',
            'Хорезмская область': 'Xorazm viloyati', 'Наманганская область': 'Наманган viloyati',
            'Навоийская область': 'Navoiy viloyati', 'Кашкадарьинская область': 'Qashqadaryo viloyati',
            'Самаркандская область': 'Samarqand viloyati', 'Сырдарьинская область': 'Sirdaryo viloyati',
            'Сурхандарьинская область': 'Surxondaryo viloyati',
            'Республика Каракалпакстан': 'Qoraqalpog\'iston Respublikasi'
        },
        'en': {
            'Tashkent City': 'Toshkent shahri', 'Tashkent Region': 'Toshkent viloyati',
            'Andijan Region': 'Andijon viloyati', 'Bukhara Region': 'Buxoro viloyati',
            'Fergana Region': 'Farg\'ona viloyati', 'Jizzakh Region': 'Jizzax viloyati',
            'Khorezm Region': 'Xorazm viloyati', 'Namangan Region': 'Namangan viloyati',
            'Navoiy Region': 'Navoiy viloyati', 'Qashqadaryo Region': 'Qashqadaryo viloyati',
            'Samarkand Region': 'Samarqand viloyati', 'Syrdarya Region': 'Sirdaryo viloyati',
            'Surxondaryo Region': 'Surxondaryo viloyati', 'Republic of Karakalpakstan': 'Qoraqalpog\'iston Respublikasi'
        }
    }

    mapped_profession = profession_mapping.get(current_lang, {}).get(profession, profession)
    mapped_city = city_mapping.get(current_lang, {}).get(city, city)

    if mapped_profession:
        builders = builders.filter(profession__icontains=mapped_profession)
    if mapped_city:
        builders = builders.filter(profile__city=mapped_city)

    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.contrib.postgres.search import TrigramSimilarity
        builders = builders.annotate(
            similarity=TrigramSimilarity('profile__user__first_name', search_query) +
                       TrigramSimilarity('profile__user__last_name', search_query) +
                       TrigramSimilarity('profile__user__username', search_query) +
                       TrigramSimilarity('bio', search_query)
        ).filter(Q(similarity__gt=0.1) | Q(profile__user__first_name__icontains=search_query) | Q(profile__user__last_name__icontains=search_query) | Q(profile__user__username__icontains=search_query)).order_by('-similarity')

    min_rating = request.GET.get('min_rating', '').strip()
    if min_rating:
        try:
            rating_val = float(min_rating)
            builders = builders.filter(rating_cache__gte=rating_val)
        except ValueError:
            pass

    posts = Post.objects.select_related('author__profile').annotate(
        likes_count=Count('likes', distinct=True)
    )
    if request.user.is_authenticated:
        try:
            user_role = request.user.profile.role
            user_city = request.user.profile.city

            if user_role in ['builder', 'team']:
                # Usta: boshqa ustalarning postlari (o'ziniki emas)
                posts = posts.filter(
                    author__profile__role__in=['builder', 'team']
                ).exclude(author=request.user)
            else:
                # Oddiy user: ustalar postlari
                posts = posts.filter(author__profile__role__in=['builder', 'team'])

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


@login_required
def workflow_list_view(request):
    profile = request.user.profile
    if profile.role == 'builder' and hasattr(profile, 'builder_info'):
        projects = profile.builder_info.assigned_projects.all()
    else:
        projects = profile.project_orders.all()
    
    # We can also fetch the review if it exists so we can display rating stars
    projects = projects.prefetch_related('review')
    
    for p in projects:
        try:
            p.has_review = bool(p.review)
        except Exception:
            p.has_review = False
            
    return render(request, 'build/workflow_list.html', {'projects': projects})


# =========================================================================
# API VIEW'LAR
# =========================================================================
class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data
        try:
            post = Post.objects.create(
                author=request.user,
                title=data.get('title', _("Qurilish e'loni")),
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
            return Response({'error': _("O'zingizning ma'lumotlaringiz.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = user.profile
            avatar_url = request.build_absolute_uri(profile.get_avatar_url())
            telegram = profile.telegram or ''
            if telegram and not telegram.startswith('@') and not telegram.startswith('t.me'):
                telegram = '@' + telegram
            whatsapp = profile.whatsapp or ''
            whatsapp_clean = ''.join(filter(str.isdigit, whatsapp))
            instagram = profile.instagram or ''
            instagram_url = instagram if instagram.startswith('http') else f"https://instagram.com/{instagram.lstrip('@')}" if instagram else ''
            facebook = profile.facebook or ''
            facebook_url = facebook if facebook.startswith('http') else f"https://facebook.com/{facebook.lstrip('@')}" if facebook else ''

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
                'instagram': instagram,
                'instagram_url': instagram_url,
                'facebook': facebook,
                'facebook_url': facebook_url,
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
        try:
            builder_profile = request.user.profile.builder_info
        except Exception:
            if request.user.profile.role == 'team':
                builder_profile = BuilderProfile.objects.create(
                    profile=request.user.profile,
                    profession=_('Kompaniya/Jamoa'),
                    experience_years=0
                )
            else:
                return Response({'error': _("Siz qurilish jamoasi emassiz!")}, status=403)

        if request.user.profile.role != 'team':
            return Response({'error': _("Siz qurilish jamoasi emassiz!")}, status=403)

        target_user = get_object_or_404(DjangoUser, id=user_id)
        if target_user == request.user:
            return Response({'error': _("O'zingizni qo'sha olmaysiz!")}, status=400)

        if builder_profile.members.filter(id=target_user.id).exists():
            return Response({'error': _("Foydalanuvchi allaqachon jamoangizda!")}, status=400)

        if target_user.joined_teams.count() >= 2:
            return Response({'error': _("Foydalanuvchi eng ko'pi bilan 2 ta jamoaga a'zo bo'lishi mumkin!")},
                            status=400)

        invite, created = TeamInvitation.objects.get_or_create(
            team=builder_profile,
            user=target_user,
            defaults={'status': 'pending'}
        )

        if not created and invite.status == 'pending':
            return Response({'error': _("Taklif allaqachon yuborilgan!")}, status=400)

        invite.status = 'pending'
        invite.save()

        room, room_created = ChatRoom.get_or_create_for(request.user, target_user)
        Message.objects.create(room=room, sender=request.user, content=f"__TEAM_INVITE__:{invite.id}")
        return Response({'success': True, 'message': _("Taklif foydalanuvchi chatiga yuborildi!")})


class RemoveTeamMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from django.contrib.auth.models import User as DjangoUser
        try:
            builder_profile = request.user.profile.builder_info
        except Exception:
            return Response({'error': _("Siz qurilish jamoasi emassiz!")}, status=403)

        if request.user.profile.role != 'team':
            return Response({'error': _("Siz qurilish jamoasi emassiz!")}, status=403)

        target_user = get_object_or_404(DjangoUser, id=user_id)
        builder_profile.members.remove(target_user)

        try:
            group_room = ChatRoom.objects.get(team_profile=builder_profile)
            group_room.participants.remove(target_user)
        except Exception:
            pass

        return Response({'success': True, 'message': _("Foydalanuvchi jamoadan o'chirildi!")})


class RespondTeamInviteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id):
        invite = get_object_or_404(TeamInvitation, id=invite_id)
        if invite.user != request.user:
            return Response({'error': _("Sizga tegishli taklif emas!")}, status=403)

        action = request.data.get('action')
        if action == 'accept':
            if invite.status != 'pending':
                return Response({'error': _("Bu taklifga allaqachon javob berilgan!")}, status=400)
            if request.user.joined_teams.count() >= 2:
                return Response({'error': _("Siz eng ko'pi bilan 2 ta jamoaga a'zo bo'lishingiz mumkin!")}, status=400)

            invite.status = 'accepted'
            invite.save()
            invite.team.members.add(request.user)

            room, room_created = ChatRoom.get_or_create_for(request.user, invite.team.profile.user)
            Message.objects.create(room=room, sender=request.user,
                                   content=_("🤝 Men jamoangizga qo'shilish taklifini qabul qildim!"))

            team_owner_name = invite.team.profile.user.get_full_name() or invite.team.profile.user.username

            group_name = _("🚀 {name} Jamoasi").format(name=team_owner_name)
            group_room, created = ChatRoom.objects.get_or_create(
                team_profile=invite.team,
                defaults={'is_group': True, 'group_name': group_name}
            )
            if created:
                group_room.participants.add(invite.team.profile.user)
            group_room.participants.add(request.user)

            Message.objects.filter(content=f"__TEAM_INVITE__:{invite.id}").update(
                content=f"__TEAM_INVITE_ACCEPTED__:{invite.id}")
            return Response({'success': True, 'message': _("Jamoaga qo'shildingiz!")})

        elif action == 'reject':
            if invite.status != 'pending':
                return Response({'error': _("Bu taklifga allaqachon javob berilgan!")}, status=400)
            invite.status = 'rejected'
            invite.save()
            room, room_created = ChatRoom.get_or_create_for(request.user, invite.team.profile.user)
            Message.objects.create(room=room, sender=request.user,
                                   content=_("❌ Men jamoangizga qo'shilish taklifini rad etdim."))
            Message.objects.filter(content=f"__TEAM_INVITE__:{invite.id}").update(
                content=f"__TEAM_INVITE_REJECTED__:{invite.id}")
            return Response({'success': True, 'message': _("Taklif rad etildi!")})

        return Response({'error': _("Noto'g'ri so'rov.")}, status=400)


@login_required
def post_edit_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        raise PermissionDenied(_("Siz ushbu e'lon muallifi emassiz!"))

    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, _("Eʼloningiz muvaffaqiyatli yangilandi!"))
            return redirect('build:profile')
    else:
        form = PostCreateForm(instance=post)

    return render(request, 'build/post_create.html', {'form': form, 'is_edit': True, 'post': post})


@login_required
def post_delete_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)

        if post.author != request.user:
            return redirect('build:profile')

        post.delete()
        messages.success(request, _("Eʼlon muvaffaqiyatli oʻchirildi!"))
    return redirect('build:profile')

@login_required
def market_pro_view(request):
    from chat.models import Message
    unread_count = Message.objects.filter(
        room__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    return render(request, 'build/marketb2bpro.html', {'unread_chat_count': unread_count})

@login_required
def leave_review_view(request, order_id):
    from django.shortcuts import redirect
    from django.contrib import messages
    
    order = get_object_or_404(ProjectOrder, id=order_id, client=request.user.profile, status='completed')
    
    if request.method == 'POST':
        # Assuming we just send a single rating from 1 to 5
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        # Make sure they haven't rated yet
        if not hasattr(order, 'review'):
            from build.models import Review
            Review.objects.create(
                order=order,
                client=request.user.profile,
                builder=order.assigned_builder,
                quality_rating=rating,
                time_rating=rating,
                politeness_rating=rating,
                comment=comment,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Ustaga bahoingiz muvaffaqiyatli saqlandi! Rahmat.")
        else:
            messages.info(request, "Siz bu ustaga avval baho bergansiz.")
            
    return redirect('build:workflow')

class NegotiateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from django.contrib.auth.models import User as DjangoUser
        from accounts.models import Notification
        target_user = get_object_or_404(DjangoUser, id=user_id)
        
        if target_user == request.user:
            return Response({'error': 'You cannot negotiate with yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
        Notification.objects.create(
            user=target_user,
            title="Kelishuv taklifi",
            message=f"{request.user.get_full_name() or request.user.username} loyiha bo'yicha siz bilan kelishish istagini bildirdi.",
            link=f"/uz/profile/{request.user.id}/"
        )
        return Response({'success': True, 'message': "Kelishuv taklifi muvaffaqiyatli yuborildi."})

class ShowInterestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from django.contrib.auth.models import User as DjangoUser
        from accounts.models import Notification
        target_user = get_object_or_404(DjangoUser, id=user_id)
        
        if target_user == request.user:
            return Response({'error': 'You cannot show interest in yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
        Notification.objects.create(
            user=target_user,
            title="Qiziqish bildirish",
            message=f"Mijoz {request.user.get_full_name() or request.user.username} sizning xizmatlaringizga qiziqish bildirdi.",
            link=f"/uz/profile/{request.user.id}/"
        )
        return Response({'success': True, 'message': "Qiziqish bildirilganligi ustaga yuborildi."})

@login_required
def mark_notifications_read(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def verify_profile_view(request):
    return render(request, 'build/profile_verify.html')

@login_required
def update_notifications_view(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return redirect('build:notifications_list')
    return redirect('build:notifications_list')

@login_required
def notifications_list_view(request):
    return render(request, 'build/notifications.html')
class UpdateTeamNameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.profile.role != 'team':
            return Response({'error': _("Siz qurilish jamoasi emassiz!")}, status=403)
        team_name = request.data.get('team_name')
        if not team_name:
            return Response({'error': _("Jamoa nomi kiritilmagan!")}, status=400)
        
        request.user.first_name = team_name
        request.user.save()
        return Response({'success': True, 'message': _("Jamoa nomi muvaffaqiyatli saqlandi!")})


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from build.models import Plan, BuilderProfile, SubscriptionRequest
from chat.models import ChatRoom, Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def plans_list(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'builder':
        return HttpResponseForbidden("Faqat quruvchilar (Builders) uchun ruxsat etilgan.")
    
    plans = Plan.objects.all().order_by('price')
    profile = getattr(request.user.profile, 'builder_info', None)
    if not profile:
        profile, _ = BuilderProfile.objects.get_or_create(profile=request.user.profile)
        
    return render(request, 'build/plans.html', {
        'plans': plans,
        'profile': profile
    })

@login_required
def choose_plan(request, plan_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'builder':
        return HttpResponseForbidden("Faqat quruvchilar uchun ruxsat etilgan.")
        
    plan = get_object_or_404(Plan, id=plan_id)
    profile = getattr(request.user.profile, 'builder_info', None)
    if not profile:
        profile, _ = BuilderProfile.objects.get_or_create(profile=request.user.profile)
        
    profile.pending_plan = plan
    profile.save()
    
    from django.urls import reverse
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        room, _ = ChatRoom.get_or_create_for(request.user, admin_user)
        return redirect(f"{reverse('chat:chat')}?room_id={room.id}")
    return redirect(reverse('chat:chat'))

@login_required
def admin_verification_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseForbidden("Faqat adminlar uchun ruxsat etilgan.")
        
    requests = SubscriptionRequest.objects.all().order_by('-created_at')
    return render(request, 'build/verification.html', {
        'requests': requests
    })

@login_required
def process_verification(request, request_id, action):
    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseForbidden("Faqat adminlar uchun ruxsat etilgan.")
        
    sub_request = get_object_or_404(SubscriptionRequest, id=request_id)
    builder_user = sub_request.user
    bp = getattr(builder_user.profile, 'builder_info', None)
    if not bp:
        bp, _ = BuilderProfile.objects.get_or_create(profile=builder_user.profile)
        
    room, _ = ChatRoom.get_or_create_for(builder_user, request.user)
    
    if action == 'accept':
        sub_request.status = 'accepted'
        sub_request.save()
        
        plan = Plan.objects.filter(name=sub_request.plan_name).first()
        duration_days = plan.duration_days if plan else 30

        bp.is_temp_active = False
        bp.subscription_status = True
        bp.subscription_plan = plan
        bp.subscription_start = timezone.now()
        bp.subscription_end = timezone.now() + timezone.timedelta(days=duration_days)
        bp.pending_plan = None
        bp.save()

        # ✅ Profile'da is_premium ni ham yoqamiz
        builder_profile_obj = builder_user.profile
        builder_profile_obj.is_premium = True
        builder_profile_obj.save(update_fields=['is_premium'])

        # ✅ Bildirishnoma yuboramiz
        from accounts.models import Notification
        Notification.objects.create(
            user=builder_user,
            title="✅ Obuna faollashtirildi!",
            message=f"Tabriklaymiz! Sizning '{sub_request.plan_name}' obunangiz admin tomonidan tasdiqlandi va faollashtirildi. Endi barcha Premium imkoniyatlardan foydalanishingiz mumkin.",
            icon='fa-solid fa-crown',
        )
        
        # Send system message & broadcast via WebSocket
        content_msg = f"✅ Tizim: To'lov tasdiqlandi. {sub_request.plan_name} tarifi doimiy faollashtirildi! Endi siz barcha Premium imkoniyatlardan foydalanishingiz mumkin."
        msg = Message.objects.create(room=room, sender=request.user, content=content_msg)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room.pk}',
            {
                'type': 'chat_message',
                'message_id': msg.id,
                'message': msg.content,
                'sender_id': request.user.id,
                'sender_name': request.user.get_full_name() or request.user.username,
                'time': msg.time_str(),
                'is_read': False,
                'room_id': room.pk,
            }
        )
        
    elif action == 'reject':
        sub_request.status = 'rejected'
        sub_request.save()
        
        bp.is_temp_active = False
        bp.subscription_status = False
        bp.subscription_plan = None
        bp.save()

        # ❌ Profile'da is_premium ni o'chiramiz
        builder_profile_obj = builder_user.profile
        builder_profile_obj.is_premium = False
        builder_profile_obj.save(update_fields=['is_premium'])

        # ❌ Rad etish bildirishnomasini yuboramiz
        from accounts.models import Notification
        Notification.objects.create(
            user=builder_user,
            title="❌ To'lov tasdiqlanmadi",
            message="Afsuski, yuborgan to'lov chekingiz tasdiqlanmadi. Iltimos, to'g'ri to'lov chekini yuboring yoki admin bilan bog'laning.",
            icon='fa-solid fa-circle-xmark',
        )
        
        # Automatic warning notification posting
        content_msg = "❌ To'lov tasdiqlanmadi. Iltimos, to'g'ri to'lov chekini yuboring yoki admin bilan bog'laning."
        msg = Message.objects.create(room=room, sender=request.user, content=content_msg)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room.pk}',
            {
                'type': 'chat_message',
                'message_id': msg.id,
                'message': msg.content,
                'sender_id': request.user.id,
                'sender_name': request.user.get_full_name() or request.user.username,
                'time': msg.time_str(),
                'is_read': False,
                'room_id': room.pk,
            }
        )
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({'success': True})
        
    return redirect('build:admin_verification_dashboard')

@login_required
def chat_room_redirect(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    room, _ = ChatRoom.get_or_create_for(other_user, request.user)
    return redirect(f"/chat/?room_id={room.id}")

@login_required
def payment_dashboard(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        # Fallback to any staff/admin
        admin_user = User.objects.filter(is_staff=True).first()
        
    room, _ = ChatRoom.get_or_create_for(request.user, admin_user)
    bp = getattr(request.user.profile, 'builder_info', None)
    if not bp:
        bp, _ = BuilderProfile.objects.get_or_create(profile=request.user.profile)
        
    if request.method == 'POST':
        plan_name = request.POST.get('plan_name')
        amount_str = request.POST.get('amount', '0')
        screenshot = request.FILES.get('screenshot')
        
        if not plan_name or not screenshot:
            return redirect('build:payment_dashboard')
            
        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0
            
        # Create SubscriptionRequest
        sub_request = SubscriptionRequest.objects.create(
            user=request.user,
            plan_name=plan_name,
            amount=amount,
            screenshot=screenshot,
            status='pending'
        )
        
        # Grant 24h temporary access and set pending plan
        plan = Plan.objects.filter(name=plan_name).first()
        bp.is_temp_active = True
        bp.temp_active_until = timezone.now() + timezone.timedelta(hours=24)
        bp.pending_plan = plan
        bp.save()
        
        # Create chat message: "To'lov cheki yuborildi"
        msg = Message.objects.create(
            room=room,
            sender=request.user,
            content="To'lov cheki yuborildi"
        )
        
        # Broadcast message via WebSocket
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{room.pk}',
                {
                    'type': 'chat_message',
                    'message_id': msg.id,
                    'message': msg.content,
                    'sender_id': request.user.id,
                    'sender_name': request.user.get_full_name() or request.user.username,
                    'time': msg.time_str(),
                    'is_read': False,
                    'room_id': room.pk,
                }
            )
        except Exception:
            pass
            
        return redirect('build:payment_dashboard')
        
    messages_list = Message.objects.filter(room=room).order_by('created_at')
    latest_request = SubscriptionRequest.objects.filter(user=request.user).order_by('-created_at').first()
    plans = Plan.objects.all().order_by('price')
    
    return render(request, 'build/payment_dashboard.html', {
        'room': room,
        'messages': messages_list,
        'bp': bp,
        'latest_request': latest_request,
        'plans': plans,
        'admin_user': admin_user
    })


# =============================================================================
# SUBSCRIPTION BACKEND: BID, PRO GRANT, STATUS CHECK
# =============================================================================

class PlaceBidAPIView(APIView):
    """Faqat aktiv obunali ustalar buyurtmaga taklif bera oladi."""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        bp = getattr(request.user.profile, 'builder_info', None)
        if not bp:
            return Response({'error': 'Siz usta profiliga ega emassiz.'}, status=403)

        # Obuna tekshiruvi
        if not bp.has_active_subscription:
            return Response({
                'error': 'subscription_required',
                'message': 'Bu funksiyadan foydalanish uchun Standard yoki Pro obuna talab etiladi.',
                'redirect': '/uz/payment-dashboard/'
            }, status=402)  # 402 Payment Required

        order = get_object_or_404(ProjectOrder, id=order_id, status='open')

        # Allaqachon taklif berganmi?
        if ProjectBid.objects.filter(order=order, builder=bp).exists():
            return Response({'error': 'Siz bu buyurtmaga allaqachon taklif bergansiz.'}, status=400)

        proposed_price = request.data.get('proposed_price')
        message = request.data.get('message', '')

        if not proposed_price:
            return Response({'error': 'Taklif narxini kiriting.'}, status=400)

        bid = ProjectBid.objects.create(
            order=order,
            builder=bp,
            proposed_price=proposed_price,
            message=message
        )

        # Mijozga bildirishnoma
        from accounts.models import Notification
        builder_name = request.user.get_full_name() or request.user.username
        Notification.objects.create(
            user=order.client.user,
            title=f"📋 Yangi taklif: {order.title}",
            message=f"{builder_name} sizning '{order.title}' buyurtmangizga {proposed_price} so'm narxida taklif berdi.",
            icon='fa-solid fa-file-invoice',
            url=f'/uz/workflow/',
        )

        return Response({'success': True, 'bid_id': bid.id, 'message': 'Taklifingiz muvaffaqiyatli yuborildi!'})


class GrantProStatusAPIView(APIView):
    """Admin tomonidan foydalanuvchiga PRO maqom beradi."""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({'error': 'Faqat adminlar uchun.'}, status=403)

        target_user = get_object_or_404(User, id=user_id)
        bp = getattr(target_user.profile, 'builder_info', None)
        if not bp:
            bp, _ = BuilderProfile.objects.get_or_create(profile=target_user.profile)

        action = request.data.get('action', 'grant')  # 'grant' yoki 'revoke'

        if action == 'grant':
            # PRO plan topamiz yoki yaratamiz
            pro_plan, _ = Plan.objects.get_or_create(
                name='PRO',
                defaults={'price': 0, 'description': 'Admin tomonidan berilgan PRO maqom', 'duration_days': 36500}
            )
            bp.subscription_status = True
            bp.subscription_plan = pro_plan
            bp.is_temp_active = False
            bp.save()

            target_user.profile.is_premium = True
            target_user.profile.save(update_fields=['is_premium'])

            from accounts.models import Notification
            Notification.objects.create(
                user=target_user,
                title="👑 Siz PRO Usta maqomini oldingiz!",
                message="Tabriklaymiz! Admin tomonidan sizga EasyBuild platformasining eng yuqori — PRO Usta maqomi berildi. Bu maqom faqat eng sara va ishonchli ustalarga beriladi.",
                icon='fa-solid fa-crown',
            )

            # Admin bilan chat orqali xabar
            room, _ = ChatRoom.get_or_create_for(target_user, request.user)
            msg = Message.objects.create(
                room=room, sender=request.user,
                content="👑 Tabriklaymiz! Sizga EasyBuild platformasining PRO Usta maqomi berildi! Siz endi platformamizning eng ishonchli ustalari qatoriga kirdingiz."
            )

            return Response({'success': True, 'message': f"{target_user.username} ga PRO maqom berildi."})

        elif action == 'revoke':
            bp.subscription_status = False
            bp.subscription_plan = None
            bp.save()

            target_user.profile.is_premium = False
            target_user.profile.save(update_fields=['is_premium'])

            return Response({'success': True, 'message': f"{target_user.username} dan PRO maqom olindi."})

        return Response({'error': 'action must be grant or revoke'}, status=400)


class CheckSubscriptionStatusAPIView(APIView):
    """Joriy foydalanuvchining obuna holatini qaytaradi."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        bp = getattr(profile, 'builder_info', None)

        data = {
            'is_premium': profile.is_premium,
            'has_active_subscription': bp.has_active_subscription if bp else False,
            'subscription_plan': bp.subscription_plan.name if (bp and bp.subscription_plan) else None,
            'is_temp_active': bp.is_temp_active if bp else False,
            'temp_active_until': bp.temp_active_until.isoformat() if (bp and bp.temp_active_until) else None,
        }
        return Response(data)
