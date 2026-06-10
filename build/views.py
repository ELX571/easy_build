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
        # Asosiy query: e'lonlar
        queryset = Post.objects.all().order_by('-is_boosted', '-created_time')

        # Filtrlar: Kategoriya va Shahar bo'yicha
        category = self.request.GET.get('category')
        city = self.request.GET.get('city')

        if category:
            queryset = queryset.filter(category=category)
        if city:
            # Ustalar yoki postlar orqali shahar bo'yicha filter
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
    return render(request, 'build/profile_edit.html', {'form': form})


# build/views.py fayliga qo'shing:
from django.contrib.auth.decorators import login_required
from .form import PostCreateForm


@login_required
def post_create_view(request):
    # Roli 'builder' bo'lmagan foydalanuvchilarni qaytarib yuboramiz
    if request.user.profile.role != 'builder':
        messages.error(request, "Xatolik! Eʼlon joylashtirish faqat Quruvchilar (Ustalar) uchun ruxsat etilgan.")
        return redirect('build:post_list')

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