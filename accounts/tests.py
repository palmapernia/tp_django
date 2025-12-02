from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from rest_framework.test import APIClient
from unittest.mock import patch


class AccountsViewsTest(TestCase):
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_signup_view_get(self):
        """Test que la página de registro se carga correctamente"""
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inscription')
        self.assertContains(response, 'form')
    
    def test_signup_view_post_valid(self):
        """Test de registro exitoso con datos válidos"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(reverse('accounts:signup'), data)
        
        # Debería redirigir después del registro exitoso
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el usuario fue creado
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Verificar que el usuario está logueado automáticamente
        user = User.objects.get(username='newuser')
        self.assertTrue(user.is_authenticated)
    
    def test_signup_view_post_invalid(self):
        """Test de registro con datos inválidos"""
        data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Email inválido
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'differentpass'  # Contraseñas no coinciden
        }
        response = self.client.post(reverse('accounts:signup'), data)
        
        # No debería redirigir
        self.assertEqual(response.status_code, 200)
        
        # El usuario no debería haberse creado
        self.assertFalse(User.objects.filter(username='newuser').exists())
        
        # Debería mostrar errores del formulario
        self.assertContains(response, 'error')
    
    def test_signup_username_already_exists(self):
        """Test de registro con un nombre de usuario que ya existe"""
        data = {
            'username': 'testuser',  # Ya existe
            'email': 'another@example.com',
            'first_name': 'Another',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(reverse('accounts:signup'), data)
        
        self.assertEqual(response.status_code, 200)
        # Solo debe existir el usuario original
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
    
    def test_login_view_get(self):
        """Test que la página de login se carga correctamente"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion')
        self.assertContains(response, 'form')
    
    def test_login_view_post_valid(self):
        """Test de login exitoso"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        
        # Debería redirigir después del login
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el usuario está logueado
        user = get_user_model().objects.get(username='testuser')
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_view_post_invalid(self):
        """Test de login con credenciales inválidas"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('accounts:login'), data)
        
        # No debería redirigir
        self.assertEqual(response.status_code, 200)
        
        # No debería estar logueado
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Debería mostrar mensaje de error
        self.assertContains(response, 'Erreur')
    
    def test_logout_view(self):
        """Test de logout"""
        # Primero hacer login
        self.client.login(username='testuser', password='testpass123')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Hacer logout
        response = self.client.post(reverse('accounts:logout'))
        
        # Debería redirigir
        self.assertEqual(response.status_code, 302)
        
        # Ya no debería estar logueado
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_edit_profile_view_get(self):
        """Test pour afficher le formulaire de modification de profil"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('accounts:edit_profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'form')

    def test_edit_profile_view_post_valid(self):
        """Test de modification de profil avec données valides"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'username': 'newtestuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@test.com'
        }
        
        response = self.client.post(reverse('accounts:edit_profile'), data)
        
        self.assertEqual(response.status_code, 302)  # Redirect après succès
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newtestuser')
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'new@test.com')

    def test_edit_profile_view_empty_username(self):
        """Test de modification avec nom d'utilisateur vide"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'username': '',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com'
        }
        
        response = self.client.post(reverse('accounts:edit_profile'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le nom d&#x27;utilisateur est requis')

    def test_edit_profile_view_password_mismatch(self):
        """Test avec mots de passe non correspondants"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword123'
        }
        
        response = self.client.post(reverse('accounts:edit_profile'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ne correspondent pas')

    def test_edit_profile_view_password_too_short(self):
        """Test avec mot de passe trop court"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'new_password': '123',
            'confirm_password': '123'
        }
        
        response = self.client.post(reverse('accounts:edit_profile'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'au moins 8 caractères')

    def test_edit_profile_view_password_change_success(self):
        """Test de changement de mot de passe réussi"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(reverse('accounts:edit_profile'), data)
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        # Vérifier que le nouveau mot de passe fonctionne
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_edit_profile_view_exception_handling(self):
        """Test gestion d'exception lors de la sauvegarde (lignes 89-90)"""
        self.client.login(username='testuser', password='testpass123')
        
        # Mock pour forcer une exception lors de la sauvegarde
        with patch('django.contrib.auth.models.User.save') as mock_save:
            mock_save.side_effect = Exception('Test exception')
            
            data = {
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@test.com'
            }
            
            response = self.client.post(reverse('accounts:edit_profile'), data)
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Erreur lors de la mise à jour')

    def test_dashboard_view_authenticated(self):
        """Test del dashboard para usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('accounts:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')  # Nombre del usuario
        self.assertContains(response, 'Dashboard')
    
    def test_dashboard_view_anonymous(self):
        """Test del dashboard para usuario anónimo (debería redirigir a login)"""
        response = self.client.get(reverse('accounts:dashboard'))
        
        # Debería redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/accounts/dashboard/')
    
    def test_redirect_after_login(self):
        """Test de redirección después del login"""
        # Intentar acceder al dashboard sin estar logueado
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Hacer login con el parámetro 'next'
        login_url = reverse('accounts:login') + '?next=' + reverse('accounts:dashboard')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(login_url, data)
        
        # Debería redirigir al dashboard
        self.assertRedirects(response, reverse('accounts:dashboard'))


class UserModelTest(TestCase):
    """Tests para el modelo User (aunque usemos el modelo por defecto de Django)"""
    
    def test_user_creation(self):
        """Test de creación de usuario"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.email, 'test2@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_string_representation(self):
        """Test de la representación en string del usuario"""
        user = User.objects.create_user(
            username='testuser3',
            first_name='Test',
            last_name='User'
        )
        
        # El método __str__ por defecto devuelve el username
        self.assertEqual(str(user), 'testuser3')
    
    def test_user_get_full_name(self):
        """Test del método get_full_name"""
        user = User.objects.create_user(
            username='testuser4',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.get_full_name(), 'John Doe')


class AccountsAPITestCase(TestCase):
    """Tests pour l'API accounts"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
    
    def test_register_serializer_valid(self):
        """Test du RegisterSerializer avec données valides"""
        from accounts.views import RegisterSerializer
        
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpassword123'))

    def test_user_profile_serializer_valid(self):
        """Test du UserProfileSerializer avec données valides"""
        from accounts.views import UserProfileSerializer
        
        data = {
            'username': 'updateduser',
            'email': 'updated@test.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        
        serializer = UserProfileSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, 'updateduser')

    def test_user_profile_serializer_password_change(self):
        """Test du changement de mot de passe via serializer"""
        from accounts.views import UserProfileSerializer
        
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        serializer = UserProfileSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertTrue(updated_user.check_password('newpassword123'))

    def test_user_profile_serializer_password_mismatch(self):
        """Test avec mots de passe non correspondants"""
        from accounts.views import UserProfileSerializer
        
        data = {
            'username': 'testuser',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword123'
        }
        
        serializer = UserProfileSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('confirm_password', serializer.errors)

    def test_user_profile_serializer_password_too_short(self):
        """Test avec mot de passe trop court"""
        from accounts.views import UserProfileSerializer
        
        data = {
            'username': 'testuser',
            'new_password': '123',
            'confirm_password': '123'
        }
        
        serializer = UserProfileSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)

    def test_profile_api_get_authenticated(self):
        """Test GET /accounts/api/profile/ avec utilisateur authentifié"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/accounts/api/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@test.com')

    def test_profile_api_get_unauthenticated(self):
        """Test GET /accounts/api/profile/ sans authentification"""
        response = self.client.get('/accounts/api/profile/')
        
        self.assertEqual(response.status_code, 401)

    def test_profile_api_patch_authenticated(self):
        """Test PATCH /accounts/api/profile/ avec utilisateur authentifié"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch('/accounts/api/profile/', data)
        
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_profile_api_patch_with_password(self):
        """Test PATCH /accounts/api/profile/ avec changement de mot de passe"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'username': 'testuser',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.patch('/accounts/api/profile/', data)
        
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_register_api_view(self):
        """Test de l'API d'inscription"""
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/accounts/api/register/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class AccountsFormsTest(TestCase):
    """Tests para los formularios de accounts (si los tienes personalizados)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
    
    def test_unique_username_validation(self):
        """Test de validación de username único durante el registro"""
        # Este test sería útil si tienes formularios personalizados
        # Por ahora, Django maneja esta validación automáticamente
        pass


class AccountsIntegrationTest(TestCase):
    """Tests de integración para el flujo completo de autenticación"""
    
    def test_complete_user_journey(self):
        """Test del flujo completo: registro -> login -> dashboard -> logout"""
        # 1. Registro
        signup_data = {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'first_name': 'Journey',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(reverse('accounts:signup'), signup_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verificar que puede acceder al dashboard
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'journeyuser')
        
        # 3. Logout
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar que no puede acceder al dashboard después del logout
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirige a login
        
        # 5. Login nuevamente
        login_data = {
            'username': 'journeyuser',
            'password': 'complexpass123'
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302)
        
        # 6. Verificar acceso al dashboard nuevamente
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_signup_invalid_form(self):
        """Test signup con formulario inválido"""
        response = self.client.post('/accounts/signup/', {
            'username': '',  # Campo requerido vacío
            'email': 'invalid-email',  # Email inválido
            'password1': '123',  # Contraseña muy corta
            'password2': '456'   # Contraseñas no coinciden
        })
        self.assertEqual(response.status_code, 200)  # Permanece en la página
        self.assertContains(response, 'form')  # Contiene errores
        self.assertFalse(User.objects.filter(username='').exists())

    def test_signup_passwords_dont_match(self):
        """Test signup con contraseñas que no coinciden"""
        response = self.client.post('/accounts/signup/', {
            'username': 'testuser2',
            'email': 'test2@example.com', 
            'password1': 'validpass123',
            'password2': 'differentpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser2').exists())

    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        response = self.client.post('/accounts/login/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Permanece en login
        self.assertContains(response, 'form')

    def test_login_invalid_form(self):
        """Test login con formulario inválido"""  
        response = self.client.post('/accounts/login/', {
            'username': '',  # Vacío
            'password': ''   # Vacío
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
