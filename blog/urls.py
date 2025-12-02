from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views_api import ArticleViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'comments', CommentViewSet)

app_name = "blog"
urlpatterns = [
    path('', views.home, name='home'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('post/', views.post_article, name='post_article'),
    path('comment/<int:article_id>/', views.post_comment, name='post_comment'),
    path('article/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('api/', include(router.urls)),
]