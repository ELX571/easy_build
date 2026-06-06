from django.urls import path

from build import views

app_name = 'build'

urlpatterns=[

    path('home/',views.PostListView.as_view(),name='home'),

]