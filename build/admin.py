from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Post, BuilderProfile, TeamInvitation,
    PortfolioItem, ProjectOrder, ProjectBid, Review,
    PostLike, PostBookmark, Plan, SubscriptionRequest, SubscriptionHistory
)


# ─── Plan ────────────────────────────────────────────────────────────────────
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_days', 'subscriber_count')
    search_fields = ('name',)

    @admin.display(description="Obunachilar")
    def subscriber_count(self, obj):
        return obj.builders.count()


# ─── SubscriptionRequest ─────────────────────────────────────────────────────
@admin.register(SubscriptionRequest)
class SubscriptionRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_user', 'plan_name', 'amount',
        'status_badge', 'screenshot_preview', 'created_at'
    )
    list_filter = ('status', 'plan_name', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'plan_name')
    readonly_fields = ('created_at', 'screenshot_preview')
    actions = ['approve_selected', 'reject_selected']

    @admin.display(description='Foydalanuvchi')
    def get_user(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.get_full_name() or obj.user.username
        )

    @admin.display(description='Holat')
    def status_badge(self, obj):
        colors = {
            'pending': ('#f59e0b', '⏳ Kutilmoqda'),
            'accepted': ('#10b981', '✅ Tasdiqlandi'),
            'rejected': ('#ef4444', '❌ Rad etildi'),
        }
        color, label = colors.get(obj.status, ('#6b7280', obj.status))
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>', color, label
        )

    @admin.display(description='Chek')
    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:60px; border-radius:6px;"/></a>',
                obj.screenshot.url, obj.screenshot.url
            )
        return '—'

    @admin.action(description='✅ Tanlangan so\'rovlarni tasdiqlash')
    def approve_selected(self, request, queryset):
        from build.models import BuilderProfile
        from accounts.models import Notification
        count = 0
        for sub_req in queryset.filter(status='pending'):
            builder_user = sub_req.user
            bp, _ = BuilderProfile.objects.get_or_create(profile=builder_user.profile)
            plan = Plan.objects.filter(name=sub_req.plan_name).first()
            duration_days = plan.duration_days if plan else 30

            sub_req.status = 'accepted'
            sub_req.save()

            bp.subscription_status = True
            bp.subscription_plan = plan
            bp.subscription_start = timezone.now()
            bp.subscription_end = timezone.now() + timezone.timedelta(days=duration_days)
            bp.is_temp_active = False
            bp.pending_plan = None
            bp.save()  # signals handle is_premium sync

            Notification.objects.create(
                user=builder_user,
                title="✅ Obuna faollashtirildi!",
                message=f"'{sub_req.plan_name}' obunangiz admin tomonidan tasdiqlandi. "
                        "Barcha Premium imkoniyatlardan foydalanishingiz mumkin!",
                icon='fa-solid fa-crown',
            )
            count += 1
        self.message_user(request, f"✅ {count} ta so'rov tasdiqlandi.")

    @admin.action(description='❌ Tanlangan so\'rovlarni rad etish')
    def reject_selected(self, request, queryset):
        from build.models import BuilderProfile
        from accounts.models import Notification
        count = 0
        for sub_req in queryset.filter(status='pending'):
            builder_user = sub_req.user
            bp, _ = BuilderProfile.objects.get_or_create(profile=builder_user.profile)

            sub_req.status = 'rejected'
            sub_req.save()

            bp.is_temp_active = False
            bp.save()  # signals handle is_premium=False sync

            Notification.objects.create(
                user=builder_user,
                title="❌ To'lov tasdiqlanmadi",
                message="Yuborgan to'lov chekingiz tasdiqlanmadi. "
                        "To'g'ri chek bilan qaytadan urinib ko'ring.",
                icon='fa-solid fa-circle-xmark',
            )
            count += 1
        self.message_user(request, f"❌ {count} ta so'rov rad etildi.")


# ─── BuilderProfile ───────────────────────────────────────────────────────────
@admin.register(BuilderProfile)
class BuilderProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_user', 'profession', 'rating_cache',
        'is_available', 'subscription_badge', 'days_remaining_display', 'gamification_status'
    )
    list_filter = ('is_available', 'subscription_status', 'subscription_plan', 'profession')
    search_fields = ('profile__user__username', 'profile__user__first_name', 'profession', 'bio')
    list_editable = ('is_available',)
    readonly_fields = ('subscription_start', 'subscription_end', 'gamification_status', 'has_active_display')
    actions = ['grant_pro', 'revoke_subscription']

    @admin.display(description='Foydalanuvchi')
    def get_user(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username

    @admin.display(description='Obuna')
    def subscription_badge(self, obj):
        if not obj.subscription_status:
            return format_html('<span style="color:#6b7280;">—</span>')
        plan_name = obj.subscription_plan.name if obj.subscription_plan else '?'
        color = '#f97316' if 'PRO' in plan_name.upper() else '#3b82f6'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>', color, plan_name
        )

    @admin.display(description='Qolgan kun')
    def days_remaining_display(self, obj):
        d = obj.days_remaining
        if d is None:
            return '—'
        if d <= 3:
            return format_html('<span style="color:#ef4444; font-weight:bold;">{} kun</span>', d)
        if d <= 7:
            return format_html('<span style="color:#f59e0b; font-weight:bold;">{} kun</span>', d)
        return format_html('<span style="color:#10b981;">{} kun</span>', d)

    @admin.display(description='Status')
    def gamification_status(self, obj):
        return obj.gamification_status

    @admin.display(description='Aktiv obuna?')
    def has_active_display(self, obj):
        return "✅ Ha" if obj.has_active_subscription else "❌ Yo'q"

    @admin.action(description='👑 PRO maqom berish')
    def grant_pro(self, request, queryset):
        from accounts.models import Notification
        pro_plan, _ = Plan.objects.get_or_create(
            name='PRO',
            defaults={'price': 0, 'description': 'Admin tomonidan berilgan PRO maqom', 'duration_days': 36500}
        )
        for bp in queryset:
            bp.subscription_status = True
            bp.subscription_plan = pro_plan
            bp.subscription_start = timezone.now()
            bp.subscription_end = None  # PRO muddatsiz
            bp.is_temp_active = False
            bp.save()  # signal syncs is_premium

            Notification.objects.create(
                user=bp.profile.user,
                title="👑 PRO Usta maqomi berildi!",
                message="Admin tomonidan sizga EasyBuild PRO Usta maqomi berildi. Tabriklaymiz!",
                icon='fa-solid fa-crown',
            )
        self.message_user(request, f"👑 {queryset.count()} ta ustaga PRO maqom berildi.")

    @admin.action(description='🚫 Obunani bekor qilish')
    def revoke_subscription(self, request, queryset):
        for bp in queryset:
            bp.subscription_status = False
            bp.subscription_plan = None
            bp.subscription_start = None
            bp.subscription_end = None
            bp.save()  # signal syncs is_premium=False
        self.message_user(request, f"🚫 {queryset.count()} ta obuna bekor qilindi.")


# ─── Post ────────────────────────────────────────────────────────────────────
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'category', 'price', 'is_boosted', 'created_time')
    list_filter = ('category', 'is_boosted', 'created_time')
    search_fields = ('title', 'description', 'author__username')
    list_editable = ('is_boosted',)
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_client', 'get_builder', 'rating', 'quality_rating', 'time_rating', 'politeness_rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('client__user__username', 'builder__profile__user__username', 'comment')
    readonly_fields = ('rating', 'ip_address', 'created_at')

    @admin.display(description='Mijoz')
    def get_client(self, obj):
        return obj.client.user.username

    @admin.display(description='Usta')
    def get_builder(self, obj):
        return obj.builder.profile.user.username


@admin.register(ProjectOrder)
class ProjectOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_client', 'status', 'budget', 'duration_days', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'client__user__username')
    list_editable = ('status',)
    date_hierarchy = 'created_at'

    @admin.display(description='Mijoz')
    def get_client(self, obj):
        return obj.client.user.username


@admin.register(ProjectBid)
class ProjectBidAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_builder', 'get_order', 'proposed_price', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('builder__profile__user__username', 'order__title')

    @admin.display(description='Usta')
    def get_builder(self, obj):
        return obj.builder.profile.user.username

    @admin.display(description='Buyurtma')
    def get_order(self, obj):
        return obj.order.title


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_builder', 'created_at')
    search_fields = ('title', 'builder__profile__user__username')

    @admin.display(description='Usta')
    def get_builder(self, obj):
        return obj.builder.profile.user.username


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_team', 'get_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')

    @admin.display(description='Jamoa')
    def get_team(self, obj):
        return obj.team.profile.user.username

    @admin.display(description='Taklif etilgan')
    def get_user(self, obj):
        return obj.user.username


admin.site.register(PostLike)
admin.site.register(PostBookmark)


# ─── SubscriptionHistory ─────────────────────────────────────────────────────
@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'event_badge', 'plan_name', 'get_performed_by', 'created_at')
    list_filter = ('event', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'plan_name')
    readonly_fields = ('user', 'event', 'plan_name', 'note', 'performed_by', 'created_at')

    @admin.display(description='Foydalanuvchi')
    def get_user(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.get_full_name() or obj.user.username
        )

    @admin.display(description='Voqea')
    def event_badge(self, obj):
        colors = {
            'activated':      ('#10b981', '✅ Faollashtirildi'),
            'expired':        ('#ef4444', '⏰ Tugadi'),
            'revoked':        ('#f97316', '🚫 Bekor qilindi'),
            'pro_granted':    ('#f59e0b', '👑 PRO berildi'),
            'pro_revoked':    ('#6b7280', '👑 PRO olindi'),
            'temp_activated': ('#3b82f6', '⏳ Vaqtincha'),
            'temp_expired':   ('#94a3b8', '⏳ Vaqtincha tugadi'),
            'renewed':        ('#8b5cf6', '🔄 Yangilandi'),
        }
        color, label = colors.get(obj.event, ('#6b7280', obj.event))
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, label)

    @admin.display(description='Kim bajargan')
    def get_performed_by(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.username
        return format_html('<span style="color:#94a3b8;">Tizim</span>')


