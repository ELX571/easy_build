from django.contrib import admin
from .models import (
    Post, BuilderProfile, TeamInvitation,
    PortfolioItem, ProjectOrder, ProjectBid, Review,
    PostLike, PostBookmark
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'category', 'price', 'is_boosted', 'created_time')
    list_filter = ('category', 'is_boosted', 'created_time')
    search_fields = ('title', 'description', 'author__username')
    list_editable = ('is_boosted',)
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)


@admin.register(BuilderProfile)
class BuilderProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'profession', 'experience_years', 'rating_cache', 'is_available', 'gamification_status')
    list_filter = ('is_available', 'profession')
    search_fields = ('profile__user__username', 'profile__user__first_name', 'profession', 'bio')
    list_editable = ('is_available',)

    @admin.display(description='Foydalanuvchi')
    def get_user(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username

    @admin.display(description='Status')
    def gamification_status(self, obj):
        return obj.gamification_status


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
