import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import admin

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )

    def __str__(self):
        return  self.question_text
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def can_vote(self):
        """Solo se puede votar si está activo"""
        return self.is_active

class Choice(models.Model):
    question = models.ForeignKey(Question,
    on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text