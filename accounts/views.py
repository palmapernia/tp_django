from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

# Imports para estadísticas
try:
    from blog.models import Article
except ImportError:
    Article = None

try:
    from polls.models import Question
except ImportError:
    Question = None

from .models import PageView, DailyVisits
from django.utils import timezone
from datetime import datetime, timedelta

# Create your views here.
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("accounts:login")

@login_required
def dashboard_view(request):
    # Obtener estadísticas si el usuario es staff
    context = {}
    if request.user.is_staff:
        # Contar usuarios
        total_users = User.objects.count()
        
        # Contar artículos del blog
        total_posts = Article.objects.count() if Article else 0
        
        # Contar sondages (questions)
        total_polls = Question.objects.count() if Question else 0
        
        # Estadísticas de visitas reales
        total_visits = PageView.objects.count()
        
        # Visitas de hoy
        today = timezone.now().date()
        today_visits = PageView.objects.filter(timestamp__date=today).count()
        
        # Visitantes únicos (últimos 30 días) - ahora por visitor_id
        thirty_days_ago = today - timedelta(days=30)
        unique_visitors = PageView.objects.filter(
            timestamp__date__gte=thirty_days_ago
        ).values('visitor_id').distinct().count()
        
        context.update({
            'total_users': total_users,
            'total_posts': total_posts,
            'total_polls': total_polls,
            'total_visits': total_visits,
            'today_visits': today_visits,
            'unique_visitors': unique_visitors,
        })
    return render(request, "accounts/dashboard.html", context)

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

@login_required
def edit_profile_view(request):
    """Vista para que los usuarios editen su perfil"""
    if request.method == 'POST':
        user = request.user
        
        # Actualizar campos del perfil
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.username = request.POST.get('username', user.username)
        
        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if new_password or confirm_password:
            if new_password != confirm_password:
                messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
                return render(request, 'accounts/edit_profile.html', {'user': request.user})
            elif len(new_password) < 8:
                messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
                return render(request, 'accounts/edit_profile.html', {'user': request.user})
            else:
                user.set_password(new_password)
                
        try:
            user.save()
            
            # Si se cambió la contraseña, volver a autenticar
            if new_password:
                login(request, user)
                messages.success(request, 'Profil et mot de passe mis à jour avec succès !')
            else:
                messages.success(request, 'Profil mis à jour avec succès !')
                
            return redirect('accounts:dashboard')
        except Exception as e:
                messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required
def my_articles_view(request):
    """Vue pour afficher les articles de l'utilisateur connecté"""
    if Article:
        user_articles = Article.objects.filter(author=request.user).prefetch_related('comments').order_by('-created_at')
    else:
        user_articles = []
    
    context = {
        'articles': user_articles,
        'title': 'Mes Articles'
    }
    return render(request, 'accounts/my_articles.html', context)

@login_required  
def my_polls_view(request):
    """Vue pour afficher les sondages de l'utilisateur connecté"""
    if Question:
        user_polls = Question.objects.filter(author=request.user).order_by('-pub_date')
    else:
        user_polls = []
        
    context = {
        'polls': user_polls,
        'title': 'Mes Sondages'
    }
    return render(request, 'accounts/my_polls.html', context)