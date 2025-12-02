from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.response import Response

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
    return render(request, "accounts/dashboard.html")

@login_required
def edit_profile_view(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        # Actualizar datos del usuario
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Validación básica
        if not request.POST.get('username'):
            messages.error(request, 'Le nom d\'utilisateur est requis.')
            return render(request, 'accounts/edit_profile.html', {'user': request.user})
        else:
            user.username = request.POST.get('username')
        
        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if new_password or confirm_password:
            # Validar contraseñas solo si al menos una fue proporcionada
            if new_password != confirm_password:
                messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
                return render(request, 'accounts/edit_profile.html', {'user': request.user})
            elif len(new_password) < 8:
                messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
                return render(request, 'accounts/edit_profile.html', {'user': request.user})
            else:
                # Cambiar la contraseña
                user.set_password(new_password)
                
        try:
            user.save()
            
            # Si se cambió la contraseña, reconectar al usuario
            if new_password:
                login(request, user)
                messages.success(request, 'Profil et mot de passe mis à jour avec succès !')
            else:
                messages.success(request, 'Profil mis à jour avec succès !')
                
            return redirect('accounts:dashboard')
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserProfileSerializer(ModelSerializer):
    """Serializer pour la modification de profil"""
    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'new_password', 'confirm_password')
        
    def validate(self, attrs):
        new_password = attrs.get('new_password', '').strip()
        confirm_password = attrs.get('confirm_password', '').strip()
        
        # Si se proporciona una contraseña, validar
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise serializers.ValidationError({'confirm_password': 'Les mots de passe ne correspondent pas.'})
            elif len(new_password) < 8:
                raise serializers.ValidationError({'new_password': 'Le mot de passe doit contenir au moins 8 caractères.'})
        
        return attrs
        
    def update(self, instance, validated_data):
        """Mettre à jour le profil utilisateur"""
        # Remover campos de contraseña de validated_data para el update normal
        new_password = validated_data.pop('new_password', '').strip()
        validated_data.pop('confirm_password', '')
        
        # Actualizar campos normales
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        
        # Cambiar contraseña si se proporciona
        if new_password:
            instance.set_password(new_password)
            
        instance.save()
        return instance
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    """Vue API pour récupérer et modifier le profil utilisateur"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def patch(self, request, *args, **kwargs):
        """Mise à jour partielle du profil"""
        return self.partial_update(request, *args, **kwargs)
    
    # def put(self, request, *args, **kwargs):
    #     """Mise à jour complète du profil"""
    #     return self.update(request, *args, **kwargs)  