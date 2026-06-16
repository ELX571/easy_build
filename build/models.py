# build/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from accounts.models import Profile  # Accounts-dan Profilni faqat shu yerda chaqiramiz


# =========================================================================
# 1. MARKET PRO (B2B E'lonlar bo'limi)
# =========================================================================
class Post(models.Model):
    CATEGORY_CHOICES = (
        ('material', 'Qurilish Materiallari bozori'),
        ('equipment', 'Texnika va Asbob-uskunalar ijarasi'),
        ('job', 'Bo\'sh ish o\'rinlari (Vakansiya)'),
        ('service', 'Xizmatlar ko\'rsatish'),
    )
    # Kelajakda Profile yoki User bilan bog'lash oson bo'lishi uchun authorni ixtiyoriy qo'shdik
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    username = models.CharField(max_length=100)
    title = models.CharField(max_length=200, default="Qurilish e'loni")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='material')
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    is_boosted = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} -> {self.title}"


# =========================================================================
# 2. QURUVCHILAR (USTALAR) PROFILLI
# =========================================================================
class BuilderProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='builder_info')
    profession = models.CharField(max_length=100, default="Usta")
    bio = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    # 🔥 OPTIMIZATSIYA: Usta qidirganda ultra-tez saralash (Sorting) va Pagination uchun kesh reyting
    rating_cache = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    def update_rating(self):
        """Reyting o'zgarganda keshni yangilovchi funksiya"""
        reviews = self.received_reviews.all()
        if reviews.exists():
            total = sum([r.rating for r in reviews])
            self.rating_cache = round(total / reviews.count(), 1)
        else:
            self.rating_cache = 0.0
        self.save()

    def __str__(self):
        return f"Usta: {self.profile.user.username} ({self.profession})"


# =========================================================================
# 3. PORTFOLYO TIZIMI (Galereya)
# =========================================================================
class PortfolioItem(models.Model):
    builder = models.ForeignKey(BuilderProfile, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='portfolio/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ish: {self.title} | {self.builder.profile.user.username}"


# =========================================================================
# 4. TENDER VA ISH JARAYONLARI (CRM / Workflow Tracker)
# =========================================================================
class ProjectOrder(models.Model):
    STATUS_CHOICES = (
        ('open', 'Ochiq (Tender)'),
        ('in_progress', 'Jarayonda (Ish boshlandi)'),
        ('review', 'Tekshirilmoqda (Mijoz nazoratida)'),
        ('completed', 'Yakunlangan'),
        ('canceled', 'Bekor qilingan'),
    )
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='project_orders')

    # ⚡️ WORKFLOW INTEGRATSIYASI: Loyihaga biriktirilgan usta (Loyiha tasdiqlangach yoziladi)
    assigned_builder = models.ForeignKey(BuilderProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='assigned_projects')

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)  # Masalan: Elektrik, Malyar, Beton xizmati
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loyiha: {self.title} [{self.get_status_display()}]"


# =========================================================================
# 5. TENDERGA TAKLIF YUBORISH (Bids System)
# =========================================================================
class ProjectBid(models.Model):
    """Ustalar ochiq tenderga o'z narxlari bilan ariza topshirish modeli"""
    order = models.ForeignKey(ProjectOrder, on_delete=models.CASCADE, related_name='bids')
    builder = models.ForeignKey(BuilderProfile, on_delete=models.CASCADE, related_name='bids')
    proposed_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Taklif qilingan narx")
    message = models.TextField(blank=True, null=True, verbose_name="Ustaning xati")
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'builder')  # Bitta usta bitta tenderga faqat 1 marta taklif bera oladi

    def __str__(self):
        return f"Taklif: {self.builder.profile.user.username} -> {self.order.title} ({self.proposed_price})"


# =========================================================================
# 6. REYTING VA FIKRLAR TIZIMI
# =========================================================================
class Review(models.Model):
    order = models.OneToOneField(ProjectOrder, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='given_reviews')
    builder = models.ForeignKey(BuilderProfile, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Reyting yozilishi bilan ustaning kesh reytingini avtomatik yangilaymiz
        self.builder.update_rating()

    def __str__(self):
        return f"{self.rating} yulduz -> Usta: {self.builder.profile.user.username}"