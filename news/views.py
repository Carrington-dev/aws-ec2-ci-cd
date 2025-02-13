from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from news.models import Post
from news.serializers import PostSerializer

class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    model = Post