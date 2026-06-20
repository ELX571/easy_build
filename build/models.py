from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from accounts.models import Profile


class Post(models.Model):
    CATEGORY_CHOICES = (
        ('material', 'Qurilish Materiallari bozori'),
        ('equipment', 'Texnika va Asbob-uskunalar ijarasi'),
        ('job', 'Bo\'sh ish o\'rinlari (Vakansiya)'),
        ('service', 'Xizmatlar ko\'rsatish'),
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts', null=True, blank=True
    )
    title = models.CharField(max_length=200, default="Qurilish e'loni")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='material')
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    is_boosted = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'E\'lon'
        verbose_name_plural = 'E\'lonlar'
        ordering = ['-is_boosted', '-created_time']

    def __str__(self):
        author_name = self.author.username if self.author else 'Noma\'lum'
        return f"{author_name} → {self.title}"


class BuilderProfile(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name='builder_info'
    )
    profession = models.CharField(max_length=100, default='Usta')
    bio = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    members = models.ManyToManyField(User, related_name='joined_teams', blank=True)
    rating_cache = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    class Meta:
        verbose_name = 'Usta Profili'
        verbose_name_plural = 'Usta Profillari'

    def update_rating(self):
        reviews = self.received_reviews.all()
        if reviews.exists():
            total = sum(r.rating for r in reviews)
            self.rating_cache = round(total / reviews.count(), 1)
        else:
            self.rating_cache = 0.0
        self.save(update_fields=['rating_cache'])

    @property
    def group_chat_room(self):
        from chat.models import ChatRoom
        return ChatRoom.objects.filter(team_profile=self).first()

    def __str__(self):
        user_name = self.profile.user.get_full_name() or self.profile.user.username
        return f"Usta: {user_name} ({self.profession})"


class TeamInvitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('accepted', 'Qabul qilindi'),
        ('rejected', 'Rad etildi'),
    )
    team = models.ForeignKey(BuilderProfile, on_delete=models.CASCADE, related_name='sent_invitations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_team_invitations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Jamoa taklifi'
        verbose_name_plural = 'Jamoa takliflari'
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.team.profile.user.username} -> {self.user.username} ({self.status})"


class PortfolioItem(models.Model):
    builder = models.ForeignKey(
        BuilderProfile, on_delete=models.CASCADE, related_name='portfolio_items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='portfolio/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolio rasmlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} | {self.builder.profile.user.username}"


class ProjectOrder(models.Model):
    STATUS_CHOICES = (
        ('open', 'Ochiq (Tender)'),
        ('in_progress', 'Jarayonda'),
        ('review', 'Tekshirilmoqda'),
        ('completed', 'Yakunlangan'),
        ('canceled', 'Bekor qilingan'),
    )

    client = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='project_orders'
    )
    assigned_builder = models.ForeignKey(
        BuilderProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_projects'
    )
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Loyiha'
        verbose_name_plural = 'Loyihalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"Loyiha: {self.title} [{self.get_status_display()}]"


class ProjectBid(models.Model):
    order = models.ForeignKey(
        ProjectOrder, on_delete=models.CASCADE, related_name='bids'
    )
    builder = models.ForeignKey(
        BuilderProfile, on_delete=models.CASCADE, related_name='bids'
    )
    proposed_price = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'builder')
        verbose_name = 'Taklif'
        verbose_name_plural = 'Takliflar'

    def __str__(self):
        return f"{self.builder.profile.user.username} → {self.order.title}"


class Review(models.Model):
    order = models.OneToOneField(
        ProjectOrder, on_delete=models.CASCADE, related_name='review'
    )
    client = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='given_reviews'
    )
    builder = models.ForeignKey(
        BuilderProfile, on_delete=models.CASCADE, related_name='received_reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sharh'
        verbose_name_plural = 'Sharhlar'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.builder.update_rating()

    def __str__(self):
        return f"{self.rating}⭐ → {self.builder.profile.user.username}"
class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"

class PostBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = 'Post Bookmark'
        verbose_name_plural = 'Post Bookmarks'

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"
