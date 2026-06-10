from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Profile # 👈 Accounts-dan Profilni faqat shu yerda chaqiramiz

# 1. ASOSIY SIZNING MODELINGIZ (B2B Market Pro e'lonlari)
class Post(models.Model):
    CATEGORY_CHOICES = (
        ('material', 'Qurilish Materiallari bozori'),
        ('equipment', 'Texnika va Asbob-uskunalar ijarasi'),
        ('job', 'Bo\'sh ish o\'rinlari (Vakansiya)'),
        ('service', 'Xizmatlar ko\'rsatish'),
    )
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


# 2. QURUVCHI PROFILLI (Faqat usta bo'lganlar uchun qo'shimcha ma'lumotlar)
class BuilderProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='builder_info')
    profession = models.CharField(max_length=100, default="Usta")
    bio = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Usta: {self.profile.user.username} ({self.profession})"


# 3. PORTFOLYO TIZIMI (Ustaning bajarilgan ishlari galereyasi)
class PortfolioItem(models.Model):
    builder = models.ForeignKey(BuilderProfile, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='portfolio/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ish: {self.title} | {self.builder.profile.user.username}"


# 4. TENDER TIZIMI (Buyurtmachilar qoldiradigan loyihalar)
class ProjectOrder(models.Model):
    STATUS_CHOICES = (
        ('open', 'Ochiq (Tender)'),
        ('in_progress', 'Jarayonda'),
        ('completed', 'Yakunlangan'),
        ('canceled', 'Bekor qilingan'),
    )
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='project_orders')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tender: {self.title} | {self.client.user.username}"


# 5. REYTING TIZIMI
class Review(models.Model):
    order = models.OneToOneField(ProjectOrder, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='given_reviews')
    builder = models.ForeignKey(BuilderProfile, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} yulduz -> Usta: {self.builder.profile.user.username}"