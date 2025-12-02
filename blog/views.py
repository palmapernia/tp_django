from django.shortcuts import render, redirect, get_object_or_404
from .models import Article, Comment
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm, CommentForm
from django.http import HttpResponseForbidden


# Create your views here.
def home(request):
    articles = Article.objects.order_by('-created_at')
    return render(request, "blog/home.html", {"articles": articles})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = Comment.objects.filter(article=article).order_by('-created_at')
    return render(request, "blog/article_detail.html", {
        "article": article,
        "comments": comments
    })

@login_required
def post_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('blog:article_detail', article_id=article.id)
    else:
        form = ArticleForm()
    return render(request, "blog/post_article.html", {"form": form})

@login_required
def post_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect('blog:article_detail', article_id=article.id)
    else:
        form = CommentForm()
    return render(request, "blog/post_comment.html", {"form": form, "article": article})

@login_required
def edit_article(request, article_id):
    article = Article.objects.get(id=article_id)

    if article.author != request.user:
        return HttpResponseForbidden("Vous n'avez pas les permissions pour éditer cet article")
    
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('blog:article_detail', article_id=article.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, "blog/edit_article.html", {"form": form, "article": article})
