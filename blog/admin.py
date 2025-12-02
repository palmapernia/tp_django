from django.contrib import admin
from .models import Article, Comment

# Register your models here.
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ['created_at']
    inlines = [CommentInline]
    search_fields = ['title']

admin.site.register(Article, ArticleAdmin)