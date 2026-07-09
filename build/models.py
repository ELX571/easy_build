from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Profile


class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    duration_days = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.name} - ${self.price}"


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
    title = models.CharField(max_length=200, blank=True, null=True)
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
    subscription_status = models.BooleanField(default=False)
    subscription_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='builders')
    is_temp_active = models.BooleanField(default=False)
    temp_active_until = models.DateTimeField(null=True, blank=True)
    pending_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_builders')

    @property
    def has_active_subscription(self):
        if self.subscription_status:
            return True
        if self.is_temp_active and self.temp_active_until and self.temp_active_until > timezone.now():
            return True
        return False
    rating_cache = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(7.0)]
    )

    class Meta:
        verbose_name = 'Usta Profili'
        verbose_name_plural = 'Usta Profillari'

    def update_rating(self):
        reviews = self.received_reviews.all()
        if not reviews.exists():
            self.rating_cache = 0.0
        else:
            # 7 yulduz tizimi: Har bir yulduz = 50 ball (Umumiy 7 * 50 = 350 ball)
            # 70 kishi 5 yulduzdan bossa (70 * 5 = 350 ball) -> 7 yulduz
            from django.db.models import Sum
            total_points = reviews.aggregate(total=Sum('rating'))['total'] or 0
            
            calculated_stars = total_points / 50.0
            
            # Maksimal 7.0 yulduz
            self.rating_cache = min(round(calculated_stars, 2), 7.0)
                
        self.save(update_fields=['rating_cache'])
        
        # Profile dagi reytingni ham yangilash (Trust Index uchun)
        self.profile.rating_average = self.rating_cache
        self.profile.save(update_fields=['rating_average'])

    @property
    def gamification_status(self):
        orders = self.profile.completed_orders_count
        rating = self.rating_cache
        
        if orders >= 100 and rating >= 4.8:
            return "Elite"
        elif orders >= 50 and rating >= 4.5:
            return "Pro"
        elif orders >= 10 and rating >= 4.0:
            return "Trusted"
        return "Newbie"
        
    @property
    def is_needs_improvement(self):
        # 3.0 dan past bo'lgan ustalar Sifatni oshirish kurslariga yuboriladi
        return self.rating_cache > 0 and self.rating_cache < 3.0

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
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        help_text="Umumiy baho (Avtomat hisoblanadi)"
    )
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=5, verbose_name="Ish sifati"
    )
    time_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=5, verbose_name="Vaqtga rioya qilish"
    )
    politeness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=5, verbose_name="Xushmuomalalik"
    )
    comment = models.TextField()
    builder_reply = models.TextField(blank=True, null=True, verbose_name="Ustaning javobi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Fake baholarni oldini olish uchun IP")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sharh'
        verbose_name_plural = 'Sharhlar'
        # 1-qoida: Bir mijoz bitta ustaga faqat 1 marta baho bera oladi
        unique_together = ('client', 'builder')

    def clean(self):
        from django.core.exceptions import ValidationError
        # 2-qoida: Faqat Yakunlangan buyurtmalargagina baho berish mumkin
        if self.order.status != 'completed':
            raise ValidationError("Baho faqat 'Yakunlangan' (completed) buyurtmalar uchun berilishi mumkin.")
        if self.order.assigned_builder != self.builder:
            raise ValidationError("Bu buyurtma ushbu ustaga tegishli emas.")

    def save(self, *args, **kwargs):
        # 3 ta yo'nalishdagi bahoning o'rtachasini olib asosiy rating ga yozamiz
        self.rating = round((self.quality_rating + self.time_rating + self.politeness_rating) / 3.0)
        self.full_clean() # clean() ni doimiy ishga tushirish uchun
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


class SubscriptionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_requests')
    plan_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    screenshot = models.ImageField(upload_to='screenshots/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan_name} (${self.amount}) - {self.status}"
