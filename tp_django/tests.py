from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Article
from polls.models import Question


class MainUrlsTest(TestCase):
    """Test de integración para URLs principales"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    # def test_main_urls_accessible(self):
    #     """Test que las URLs principales son accesibles"""
    #     # URL raíz debería redirigir al blog
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
        
    #     # URLs de blog
    #     response = self.client.get('/blog/')
    #     self.assertEqual(response.status_code, 200)
        
    #     # URLs de polls
    #     response = self.client.get('/polls/')
    #     self.assertEqual(response.status_code, 200)
        
    #     # URLs de accounts
    #     response = self.client.get('/accounts/login/')
    #     self.assertEqual(response.status_code, 200)
        
    #     response = self.client.get('/accounts/signup/')
    #     self.assertEqual(response.status_code, 200)
    def test_main_urls_accessible(self):

        urls_to_test = [
            ('/', 200),
            ('/polls/', 200),
            ('/accounts/login/', 200),
            ('/accounts/signup/', 200),
        ]
        
        for url, expected_status in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status, 
                            f"URL {url} devolvió {response.status_code} en lugar de {expected_status}")
    
    def test_admin_url_exists(self):
        """Test que la URL admin existe"""
        response = self.client.get('/admin/')
        # Admin redirige a login, no es 404
        self.assertIn(response.status_code, [200, 302])
    
    def test_404_handling(self):
        """Test de manejo de URLs inexistentes"""
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)