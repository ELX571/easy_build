from rest_framework import serializers
from build.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'description', 'image']
        
    def create(self, validated_data):
        user = self.context['request'].user
        # Soddalashtirilgan e'lon uchun default qadriyatlar
        validated_data['author'] = user
        validated_data['category'] = "service"
        return super().create(validated_data)
