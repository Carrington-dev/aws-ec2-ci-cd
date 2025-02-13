from rest_framework.serializers import ModelSerializer

from news.models import Post

class PostSerializer(ModelSerializer):
    class Meta:
        fields = ["title", "content", "date_posted"]
        model = Post