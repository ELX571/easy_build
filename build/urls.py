from django.urls import path
from build import views

app_name = 'build'

urlpatterns = [
    # =========================================================================
    # 1. BOSH SAHIFA & USTA QIDIRISH HUBI
    # =========================================================================
    path('', views.BuilderListView.as_view(), name='home'),

    # =========================================================================
    # 2. MARKET PRO (B2B MARKETPLACE - READ ONLY)
    # =========================================================================
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('market/create/', views.post_create_view, name='post_create'),

    # 🔥 FONDA JONLI LIVE QIDIRUV DROPDOWN RO'YXATI UCHUN API YO'LI
    path('api/market-search/', views.market_live_search_api, name='market_live_search_api'),

    # =========================================================================
    # 🔥 EXCLUSIVE CRUD CONTROL APIS (FAQAT PROFIL ICHIDA ISHLAYDI)
    # =========================================================================
    path('market/post/<int:post_id>/edit/', views.post_edit_api, name='post_edit_api'),
    path('market/post/<int:post_id>/delete/', views.post_delete_api, name='post_delete_api'),

    # =========================================================================
    # 3. ISH JARAYONLARI TIZIMI (CRM / KANBAN PROGRESS TRACKING)
    # =========================================================================
    path('workspace/', views.ProjectWorkflowListView.as_view(), name='workflow_list'),
    path('bid/accept/<int:bid_id>/', views.accept_builder_bid_view, name='accept_bid'),
    path('project/<int:project_id>/status/<str:status_slug>/', views.update_workflow_status_view, name='update_status'),

    # =========================================================================
    # 4. FOYDALANUVCHI PROFILI SOZLAMALARI & DASHBOARD
    # =========================================================================
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    #---#---#---#---#----#---#---#---#---#
]