from django.shortcuts import render
from django.views.generic import ListView
from build.models import Post

class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'home_page'

