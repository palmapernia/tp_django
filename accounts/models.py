from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class PageView(models.Model):
    """Modelo para trackear visitas a páginas"""
    url = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)
    visitor_id = models.CharField(max_length=36, blank=True, help_text="UUID único por visitante")
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.url} - {self.timestamp}"

class DailyVisits(models.Model):
    """Modelo para almacenar estadísticas diarias de visitas"""
    date = models.DateField(unique=True)
    total_visits = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.date} - {self.total_visits} visitas"
