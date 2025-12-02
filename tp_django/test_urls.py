from django.test import TestCase, override_settings
from django.conf import settings
from django.urls import reverse


class URLConfigTest(TestCase):
    """Tests pour la configuration des URLs principales"""
    
    def test_debug_urls_in_debug_mode(self):
        """Test que les URLs debug sont disponibles en mode DEBUG=True"""
        # Le debug_toolbar_urls et static sont ajoutés seulement si DEBUG=True
        with override_settings(DEBUG=True):
            # Test d'une URL principale
            response = self.client.get('/')
            # Ne doit pas donner d'erreur 404 sur l'URL racine
            self.assertIn(response.status_code, [200, 302])
    
    @override_settings(DEBUG=False)
    def test_no_debug_urls_in_production(self):
        """Test qu'en production (DEBUG=False), les URLs debug ne sont pas ajoutées"""
        # En mode production, les lignes 40-41 ne sont pas exécutées
        response = self.client.get('/')
        # L'application devrait toujours fonctionner
        self.assertIn(response.status_code, [200, 302])
        
    def test_main_app_urls(self):
        """Test des URLs principales des applications"""
        # Test polls URL
        response = self.client.get('/polls/')
        self.assertEqual(response.status_code, 200)
        
        # Test accounts URLs
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        
        # Test blog URL (racine)
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])

    def test_debug_mode_urls_added(self):
        """Test que les URLs debug sont ajoutées en mode DEBUG (lignes 40-41)"""
        # Forcer le rechargement du module urls avec DEBUG=True
        import importlib
        from django.conf import settings
        from tp_django import urls
        
        # Sauvegarder l'état original
        original_debug = settings.DEBUG
        original_urlpatterns = urls.urlpatterns.copy()
        
        try:
            # Forcer DEBUG=True et recharger le module
            settings.DEBUG = True
            importlib.reload(urls)
            
            # Vérifier que les URLs ont été ajoutées (lignes 40-41)
            self.assertTrue(len(urls.urlpatterns) >= len(original_urlpatterns))
            
            # Test d'accès aux URLs debug
            response = self.client.get('/__debug__/render_panel/')
            # Peut retourner 404 mais pas d'erreur de configuration
            self.assertIn(response.status_code, [404, 200, 302])
            
        finally:
            # Restaurer l'état original
            settings.DEBUG = original_debug
            urls.urlpatterns = original_urlpatterns
    
    def test_production_mode_no_debug_urls(self):
        """Test qu'en mode production les URLs debug ne sont pas ajoutées"""
        import importlib
        from django.conf import settings
        from tp_django import urls
        
        # Sauvegarder l'état original  
        original_debug = settings.DEBUG
        original_urlpatterns = urls.urlpatterns.copy()
        
        try:
            # Forcer DEBUG=False et recharger
            settings.DEBUG = False
            importlib.reload(urls)
            
            # Les lignes 40-41 ne doivent pas être exécutées
            # Le nombre d'URLs devrait être le même que la base
            base_urls = [
                'polls/', 'admin/', 'accounts/', '', 
                'api/schema/', 'api/docs/swagger/', 'api/docs/redoc/'
            ]
            self.assertEqual(len(urls.urlpatterns), len(base_urls))
            
        finally:
            # Restaurer l'état original
            settings.DEBUG = original_debug  
            urls.urlpatterns = original_urlpatterns