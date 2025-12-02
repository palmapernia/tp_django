from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Comment
        fields = ['id', 'article', 'author', 'author_username', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']

class ArticleSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_username', 'created_at', 'image', 'comments']
        read_only_fields = ['author', 'created_at']