from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = CloudinaryField('image', folder='articles', blank=True, null=True)

    def __str__(self):
        return self.title
    
    @property
    def summary(self):
        """Retourne un résumé de l'article basé sur le contenu"""
        return self.content[:150] + "..." if len(self.content) > 150 else self.content
    
class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.author.username} sur {self.article.title}"