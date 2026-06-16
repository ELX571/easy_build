from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.humanize.templatetags.humanize import intcomma

from accounts.models import Profile
from accounts.form import ProfileEditForm
from .models import Post, BuilderProfile, ProjectOrder, ProjectBid
from .form import PostCreateForm

# =========================================================================
# GLOBAL CONSTANTS (SPRAVOCHNIK MA'LUMOTLARI)
# =========================================================================
UZB_REGIONS = [
    "Toshkent shahri", "Toshkent viloyati", "Andijon viloyati",
    "Buxoro viloyati", "Farg'ona viloyati", "Jizzax viloyati",
    "Xorazm viloyati", "Namangan viloyati", "Navoiy viloyati",
    "Qashqadaryo viloyati", "Samarqand viloyati", "Sirdaryo viloyati",
    "Surxondaryo viloyati", "Qoraqalpog'iston Respublikasi"
]

CONSTRUCTION_PROFESSIONS = [
    "Elektrik", "Santexnik", "Betonchi / Armaturachi",
    "Suvoqchi / Malyar", "Kafelchi (Plitkach)", "Payvandchi (Svarshik)",
    "Tom yopuvchi (Tomchi)", "G'isht quyuvchi (G'ishtchi)", "Duradgor / Yog'och ustasi",
    "Gipsokartonchi", "Isitish va Sovutish (HVAC)", "Loyiha muhandisi (Prorab)",
    "Fasad ustasi", "Demontaj / Buzish ishlari", "Umumiy quruvchi"
]


# =========================================================================
# 1. USTA QIDIRISH HUBI (Advanced Search, Filter & Pagination)
# =========================================================================
class BuilderListView(ListView):
    model = BuilderProfile
    template_name = 'build/home.html'
    context_object_name = 'builders'
    paginate_by = 6

    def get_queryset(self):
        queryset = BuilderProfile.objects.filter(is_available=True).select_related('profile__user')

        search_query = self.request.GET.get('search', '')
        profession = self.request.GET.get('profession', '')
        city = self.request.GET.get('city', '')
        min_rating = self.request.GET.get('min_rating', '')

        if search_query:
            queryset = queryset.filter(
                Q(profile__user__first_name__icontains=search_query) |
                Q(profile__user__last_name__icontains=search_query) |
                Q(bio__icontains=search_query)
            )
        if profession:
            queryset = queryset.filter(profession=profession)
        if city:
            queryset = queryset.filter(profile__city=city)
        if min_rating:
            queryset = queryset.filter(rating_cache__gte=float(min_rating))

        return queryset.order_by('-rating_cache', '-experience_years')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_profession'] = self.request.GET.get('profession', '')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_min_rating'] = self.request.GET.get('min_rating', '')
        context['all_professions'] = CONSTRUCTION_PROFESSIONS
        context['all_cities'] = UZB_REGIONS
        return context


# =========================================================================
# 2. MARKET PRO (B2B E'lonlar bo'limi - READ ONLY LIST)
# =========================================================================
class PostListView(ListView):
    model = Post
    template_name = 'build/marketb2bpro.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-is_boosted', '-created_time')
        category = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        if category:
            queryset = queryset.filter(category=category)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


@login_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.username = request.user.username
            post.save()
            return redirect('build:post_list')
    else:
        form = PostCreateForm()
    return render(request, 'build/post_create.html', {'form': form})


# =========================================================================
# 🔥 MARKET PRO - JONLI LIVE QIDIRUV API (NO-REFRESH DROPDOWN)
# =========================================================================
def market_live_search_api(request):
    search_query = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    posts = Post.objects.all().order_by('-is_boosted', '-created_time')

    if category:
        posts = posts.filter(category=category)
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    posts_data = []
    for post in posts[:10]:
        posts_data.append({
            'title': post.title or "Sarlavhasiz e'lon",
            'description': post.description or "",
            'author': f"@{post.author.username}" if post.author else f"@{post.username}",
            'date': post.created_time.strftime('%d.%m.%Y') if post.created_time else "",
            'price': f"{intcomma(post.price)} UZS" if post.price else "Kelishilgan narx",
            'img_url': post.image.url if post.image else "",
            'category_display': post.get_category_display()
        })
    return JsonResponse({'posts': posts_data})


# =========================================================================
# 🔥 PROFILE MANAGEMENT CONTROLS - EXCLUSIVE EDIT & DELETE APIS (CRUD)
# =========================================================================
@login_required
def post_edit_api(request, post_id):
    """ Profil ichida exclusive ishlaydigan tahrirlash API logikasi """
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return JsonResponse({'success': False, 'message': 'Sizda bu eʼlonni oʻzgartirish huquqi yoʻq!'}, status=403)

    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Eʼlon muvaffaqiyatli oʻzgartirildi!'})
        return JsonResponse({'success': False, 'message': 'Formada xatolik bor!', 'errors': form.errors})

    return JsonResponse({'success': False, 'message': 'Notoʻgʻri soʻrov!'}, status=400)


@require_POST
@login_required
def post_delete_api(request, post_id):
    """ Profil ichida exclusive ishlaydigan GitHub-Style xavfsiz o'chirish API logikasi """
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return JsonResponse({'success': False, 'message': 'Sizda bu eʼlonni oʻchirish huquqi yoʻq!'}, status=403)

    post.delete()
    return JsonResponse({'success': True, 'message': 'Eʼlon butunlay oʻchirildi!'})


# =========================================================================
# 3. ISH JARRAYONLARI TIZIMI (CRM / Workflow Tracker)
# =========================================================================
class ProjectWorkflowListView(LoginRequiredMixin, ListView):
    model = ProjectOrder
    template_name = 'build/workflow_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        profile = self.request.user.profile
        if profile.role == 'client':
            return ProjectOrder.objects.filter(client=profile).order_by('-created_at')
        elif profile.role == 'builder':
            return ProjectOrder.objects.filter(assigned_builder__profile=profile).order_by('-created_at')
        return ProjectOrder.objects.none()


@login_required
def accept_builder_bid_view(request, bid_id):
    bid = get_object_or_404(ProjectBid, id=bid_id)
    project = bid.order

    if project.client != request.user.profile:
        messages.error(request, "Ruxsat berilmagan harakat!")
        return redirect('build:workflow_list')

    if project.status == 'open':
        bid.is_accepted = True
        bid.save()

        project.assigned_builder = bid.builder
        project.budget = bid.proposed_price
        project.status = 'in_progress'
        project.save()

        bid.builder.is_available = False
        bid.builder.save()

        messages.success(request,
                         f"Loyiha tasdiqlandi! {bid.builder.profile.user.username} bilan ish jarayon boshlandi.")
    else:
        messages.warning(request, "Bu loyiha allaqachon faol jarayonda yoki yakunlangan.")

    return redirect('build:workflow_list')


@login_required
def update_workflow_status_view(request, project_id, status_slug):
    project = get_object_or_404(ProjectOrder, id=project_id)
    profile = request.user.profile

    if project.client != profile and project.assigned_builder != profile.builder_info:
        messages.error(request, "Bu loyiha boshqaruviga huquqingiz yo'q!")
        return redirect('build:workflow_list')

    if status_slug == 'review' and project.status == 'in_progress' and profile.role == 'builder':
        project.status = 'review'
        project.save()
        messages.success(request, "Loyiha mijozga tekshirish uchun yuborildi.")

    elif status_slug == 'completed' and project.status == 'review' and profile.role == 'client':
        project.status = 'completed'
        project.save()

        project.assigned_builder.is_available = True
        project.assigned_builder.save()
        messages.success(request, "Loyiha muvaffaqiyatli yakunlandi! Ustaga baho berishingiz mumkin.")

    return redirect('build:workflow_list')


# =========================================================================
# 4. FOYDALANUVCHI PROFILI (Dashboard)
# =========================================================================
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    # 🔥 TO'G'RILANDI: Profil ichidagi "Mening e'lonlarim" ishlashi uchun shaxsiy postlarni filtrlab uzatamiz
    my_posts = Post.objects.filter(author=request.user).order_by('-created_time')

    context = {
        'profile': profile,
        'my_posts': my_posts
    }
    return render(request, 'build/profile.html', context)


@login_required
def profile_edit_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
            return redirect('build:profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'build/profile_edit.html', {'form': form})