from django.db import models

class Post(models.Model):
    username = models.CharField(max_length = 100)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
