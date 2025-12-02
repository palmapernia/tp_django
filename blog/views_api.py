from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    @extend_schema(
        request={'multipart/form-data': ArticleSerializer}
    )

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        request={'multipart/form-data': ArticleSerializer}
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        request={'multipart/form-data': ArticleSerializer}
    )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        request={'multipart/form-data': ArticleSerializer}
    )

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)