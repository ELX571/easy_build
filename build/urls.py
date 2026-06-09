from django.urls import path

from build import views

app_name = 'build'

urlpatterns=[

    path('',views.PostListView.as_view(),name='home'),
    path('profile/',views.profile_view,name='profile'),
    path('profile/edit/',views.profile_edit_view,name='profile_edit'),

]