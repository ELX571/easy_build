from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_username', 'get_full_name', 'role', 'city',
        'is_verified', 'is_premium', 'rating_average', 'trust_index_display',
        'completed_orders_count', 'created_at'
    )
    list_filter = ('role', 'city', 'is_verified', 'is_premium')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_editable = ('is_verified', 'is_premium', 'role')
    readonly_fields = ('created_at', 'trust_index_display')
    ordering = ('-created_at',)

    @admin.display(description='Username')
    def get_username(self, obj):
        return obj.user.username

    @admin.display(description='Ism Familiya')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or '—'

    @admin.display(description='Trust Index')
    def trust_index_display(self, obj):
        return f"{obj.trust_index}/100"
