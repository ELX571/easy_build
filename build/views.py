from django.shortcuts import render
from django.views.generic import ListView
from build.models import Post

class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'home_page'


from accounts.models import Profile

def profile_view(request):
    # Foydalanuvchi tizimga kirmagan bo'lsa login pageda qaytarish
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('accounts:login')
        
    # Foydalanuvchining profilini olish
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
        
    return render(request, 'build/profile.html', {'profile': profile})

from accounts.form import SecondRegisterForm

def profile_edit_view(request):
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('accounts:login')
        
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('build:home')
        
    if request.method == 'POST':
        form = SecondRegisterForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            from django.shortcuts import redirect
            return redirect('build:profile')
    else:
        form = SecondRegisterForm(instance=profile)
        
    return render(request, 'build/profile_edit.html', {'form': form})