from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from blog.models import Article, Comment
from blog.forms import ArticleForm, CommentForm
from io import BytesIO
from PIL import Image
import tempfile


class ArticleModelTest(TestCase):
    """Tests para el modelo Article"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_article_creation(self):
        """Test de creación de artículo"""
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article content.',
            author=self.user
        )
        
        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(article.content, 'This is a test article content.')
        self.assertEqual(article.author, self.user)
        self.assertIsNotNone(article.created_at)
    
    def test_article_string_representation(self):
        """Test de la representación en string del artículo"""
        article = Article.objects.create(
            title='My Test Article',
            content='Content here',
            author=self.user
        )
        
        self.assertEqual(str(article), 'My Test Article')
    
    def test_article_with_image(self):
        """Test de artículo con imagen"""
        # Crear una imagen temporal
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = BytesIO()
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        
        uploaded_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=temp_file.read(),
            content_type='image/jpeg'
        )
        
        article = Article.objects.create(
            title='Article with Image',
            content='This article has an image',
            author=self.user,
            image=uploaded_image
        )
        
        self.assertTrue(article.image)
        self.assertIn('test_image', article.image.name)


class CommentModelTest(TestCase):
    """Tests para el modelo Comment"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Content for testing comments',
            author=self.user
        )
    
    def test_comment_creation(self):
        """Test de creación de comentario"""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='This is a test comment'
        )
        
        self.assertEqual(comment.article, self.article)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertIsNotNone(comment.created_at)
    
    def test_comment_string_representation(self):
        """Test de la representación en string del comentario"""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Comment content'
        )
        
        expected = f'Commentaire par {self.user.username} sur {self.article.title}'
        self.assertEqual(str(comment), expected)


class BlogViewsTest(TestCase):
    """Tests para las vistas del blog"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='This is test content for the article.',
            author=self.user
        )
    
    def test_home_view_get(self):
        """Test de la vista home (lista de artículos)"""
        response = self.client.get(reverse('blog:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
        self.assertContains(response, self.user.username)
    
    def test_home_view_with_multiple_articles(self):
        """Test de la vista home con múltiples artículos"""
        Article.objects.create(
            title='Second Article',
            content='Second article content',
            author=self.user
        )
        Article.objects.create(
            title='Third Article',
            content='Third article content',
            author=self.user
        )
        
        response = self.client.get(reverse('blog:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
        self.assertContains(response, 'Second Article')
        self.assertContains(response, 'Third Article')
    
    def test_article_detail_view(self):
        """Test de la vista de detalle de artículo"""
        response = self.client.get(reverse('blog:article_detail', args=[self.article.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.content)
        self.assertContains(response, self.user.username)
    
    def test_article_detail_view_nonexistent(self):
        """Test de vista de detalle con artículo inexistente"""
        response = self.client.get(reverse('blog:article_detail', args=[9999]))
        
        self.assertEqual(response.status_code, 404)
    
    def test_post_article_view_get_authenticated(self):
        """Test de la vista de crear artículo (GET) para usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('blog:post_article'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Créer un nouvel article')
        self.assertIsInstance(response.context['form'], ArticleForm)
    
    def test_post_article_view_get_anonymous(self):
        """Test de la vista de crear artículo (GET) para usuario anónimo"""
        response = self.client.get(reverse('blog:post_article'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/post/')
    
    def test_post_article_view_post_valid(self):
        """Test de creación de artículo con datos válidos"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'New Article',
            'content': 'This is the content of the new article.'
        }
        response = self.client.post(reverse('blog:post_article'), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el artículo fue creado
        new_article = Article.objects.get(title='New Article')
        self.assertEqual(new_article.content, 'This is the content of the new article.')
        self.assertEqual(new_article.author, self.user)
        
        # Verificar redirección al detalle del artículo
        self.assertRedirects(response, reverse('blog:article_detail', args=[new_article.id]))
    
    def test_post_article_view_post_invalid(self):
        """Test de creación de artículo con datos inválidos"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': '',  # Título vacío
            'content': 'Content without title'
        }
        response = self.client.post(reverse('blog:post_article'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
    
    def test_edit_article_view_get_owner(self):
        """Test de la vista de editar artículo (GET) para el propietario"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('blog:edit_article', args=[self.article.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modifier l\'article')
        self.assertIsInstance(response.context['form'], ArticleForm)
        self.assertEqual(response.context['article'], self.article)
    
    def test_edit_article_view_get_non_owner(self):
        """Test de la vista de editar artículo (GET) para no propietario"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.get(reverse('blog:edit_article', args=[self.article.id]))
        
        self.assertEqual(response.status_code, 403)
    
    def test_edit_article_view_post_valid(self):
        """Test de edición de artículo con datos válidos"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'Updated Article Title',
            'content': 'Updated content for the article.'
        }
        response = self.client.post(reverse('blog:edit_article', args=[self.article.id]), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el artículo fue actualizado
        updated_article = Article.objects.get(id=self.article.id)
        self.assertEqual(updated_article.title, 'Updated Article Title')
        self.assertEqual(updated_article.content, 'Updated content for the article.')
        
        # Verificar redirección al detalle del artículo
        self.assertRedirects(response, reverse('blog:article_detail', args=[self.article.id]))
    
    def test_post_comment_view_get_authenticated(self):
        """Test de la vista de crear comentario (GET) para usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('blog:post_comment', args=[self.article.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajouter un commentaire')
        self.assertContains(response, self.article.title)
        self.assertIsInstance(response.context['form'], CommentForm)
    
    def test_post_comment_view_get_anonymous(self):
        """Test de la vista de crear comentario (GET) para usuario anónimo"""
        response = self.client.get(reverse('blog:post_comment', args=[self.article.id]))
        
        self.assertEqual(response.status_code, 302)
    
    def test_post_comment_view_post_valid(self):
        """Test de creación de comentario con datos válidos"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'content': 'This is a test comment on the article.'
        }
        response = self.client.post(reverse('blog:post_comment', args=[self.article.id]), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el comentario fue creado
        comment = Comment.objects.get(content='This is a test comment on the article.')
        self.assertEqual(comment.article, self.article)
        self.assertEqual(comment.author, self.user)
        
        # Verificar redirección al detalle del artículo
        self.assertRedirects(response, reverse('blog:article_detail', args=[self.article.id]))
    
    def test_post_comment_view_nonexistent_article(self):
        """Test de crear comentario en artículo inexistente"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('blog:post_comment', args=[9999]))
        
        self.assertEqual(response.status_code, 404)


class BlogFormsTest(TestCase):
    """Tests para los formularios del blog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=self.user
        )
    
    def test_article_form_valid_data(self):
        """Test del formulario de artículo con datos válidos"""
        form_data = {
            'title': 'Test Article Title',
            'content': 'This is the content of the test article.'
        }
        form = ArticleForm(data=form_data)
        
        self.assertTrue(form.is_valid())
    
    def test_article_form_no_data(self):
        """Test del formulario de artículo sin datos"""
        form = ArticleForm(data={})
        
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('content', form.errors)
    
    def test_article_form_save(self):
        """Test de guardado del formulario de artículo"""
        form_data = {
            'title': 'Form Test Article',
            'content': 'Content from form test.'
        }
        form = ArticleForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        article = form.save(commit=False)
        article.author = self.user
        article.save()
        
        saved_article = Article.objects.get(title='Form Test Article')
        self.assertEqual(saved_article.content, 'Content from form test.')
        self.assertEqual(saved_article.author, self.user)
    
    def test_comment_form_valid_data(self):
        """Test del formulario de comentario con datos válidos"""
        form_data = {
            'content': 'This is a test comment content.'
        }
        form = CommentForm(data=form_data)
        
        self.assertTrue(form.is_valid())
    
    def test_comment_form_no_data(self):
        """Test del formulario de comentario sin datos"""
        form = CommentForm(data={})
        
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
    
    def test_comment_form_save(self):
        """Test de guardado del formulario de comentario"""
        form_data = {
            'content': 'Comment from form test.'
        }
        form = CommentForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        comment = form.save(commit=False)
        comment.article = self.article
        comment.author = self.user
        comment.save()
        
        saved_comment = Comment.objects.get(content='Comment from form test.')
        self.assertEqual(saved_comment.article, self.article)
        self.assertEqual(saved_comment.author, self.user)


class BlogIntegrationTest(TestCase):
    """Tests de integración para el flujo completo del blog"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='bloguser',
            email='blog@example.com',
            password='blogpass123',
            first_name='Blog',
            last_name='User'
        )
    
    def test_complete_blog_workflow(self):
        """Test del flujo completo: login -> crear artículo -> ver detalle -> comentar -> editar"""
        # 1. Login
        login_data = {
            'username': 'bloguser',
            'password': 'blogpass123'
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Crear artículo
        article_data = {
            'title': 'Integration Test Article',
            'content': 'This article is for integration testing purposes.'
        }
        response = self.client.post(reverse('blog:post_article'), article_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el artículo fue creado
        article = Article.objects.get(title='Integration Test Article')
        
        # 3. Ver detalle del artículo
        response = self.client.get(reverse('blog:article_detail', args=[article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Article')
        
        # 4. Añadir comentario
        comment_data = {
            'content': 'This is an integration test comment.'
        }
        response = self.client.post(reverse('blog:post_comment', args=[article.id]), comment_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el comentario fue creado
        comment = Comment.objects.get(content='This is an integration test comment.')
        self.assertEqual(comment.article, article)
        
        # 5. Editar artículo
        edit_data = {
            'title': 'Updated Integration Test Article',
            'content': 'This article content has been updated during integration testing.'
        }
        response = self.client.post(reverse('blog:edit_article', args=[article.id]), edit_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el artículo fue actualizado
        updated_article = Article.objects.get(id=article.id)
        self.assertEqual(updated_article.title, 'Updated Integration Test Article')
        
        # 6. Ver home con el artículo actualizado
        response = self.client.get(reverse('blog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Updated Integration Test Article')
    
    def test_anonymous_user_restrictions(self):
        """Test de restricciones para usuarios anónimos"""
        # Los usuarios anónimos pueden ver home
        response = self.client.get(reverse('blog:home'))
        self.assertEqual(response.status_code, 200)
        
        # Los usuarios anónimos pueden ver detalles de artículos
        article = Article.objects.create(
            title='Public Article',
            content='This is public content',
            author=self.user
        )
        response = self.client.get(reverse('blog:article_detail', args=[article.id]))
        self.assertEqual(response.status_code, 200)
        
        # Los usuarios anónimos NO pueden crear artículos
        response = self.client.get(reverse('blog:post_article'))
        self.assertEqual(response.status_code, 302)  # Redirige a login
        
        # Los usuarios anónimos NO pueden crear comentarios
        response = self.client.get(reverse('blog:post_comment', args=[article.id]))
        self.assertEqual(response.status_code, 302)  # Redirige a login
        
        # Los usuarios anónimos NO pueden editar artículos
        response = self.client.get(reverse('blog:edit_article', args=[article.id]))
        self.assertEqual(response.status_code, 302)  # Redirige a login


class BlogAPITestCase(TestCase):
    """Tests pour l'API blog"""
    
    def setUp(self):
        from rest_framework.test import APIClient
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='other@test.com'
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=self.user
        )
        
        self.comment = Comment.objects.create(
            article=self.article,
            content='Test comment',
            author=self.user
        )
        
        self.client = APIClient()

    def test_is_author_or_readonly_permission_safe_methods(self):
        """Test permission pour méthodes sûres"""
        from blog.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'GET'
        request.user = self.other_user
        
        self.assertTrue(permission.has_object_permission(request, None, self.article))

    def test_is_author_or_readonly_permission_author(self):
        """Test permission pour l'auteur"""
        from blog.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'DELETE'
        request.user = self.user
        
        self.assertTrue(permission.has_object_permission(request, None, self.article))

    def test_is_author_or_readonly_permission_not_author(self):
        """Test permission pour non-auteur"""
        from blog.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'DELETE'
        request.user = self.other_user
        
        self.assertFalse(permission.has_object_permission(request, None, self.article))

    def test_article_viewset_list(self):
        """Test GET /api/articles/"""
        response = self.client.get('/api/articles/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_article_viewset_create_authenticated(self):
        """Test POST /api/articles/ avec authentification"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'New Article',
            'content': 'New content'
        }
        
        response = self.client.post('/api/articles/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], self.user.id)

    def test_article_viewset_perform_create(self):
        """Test perform_create assigne automatiquement l'auteur"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Another Article',
            'content': 'Another content'
        }
        
        response = self.client.post('/api/articles/', data)
        
        self.assertEqual(response.status_code, 201)
        created_article = Article.objects.get(id=response.data['id'])
        self.assertEqual(created_article.author, self.user)

    def test_comment_viewset_list(self):
        """Test GET /api/comments/"""
        response = self.client.get('/api/comments/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_comment_viewset_create_authenticated(self):
        """Test POST /api/comments/ avec authentification"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'article': self.article.id,
            'content': 'New comment'
        }
        
        response = self.client.post('/api/comments/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], self.user.id)

    def test_comment_viewset_perform_create(self):
        """Test perform_create pour commentaires assigne l'auteur"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'article': self.article.id,
            'content': 'Another comment'
        }
        
        response = self.client.post('/api/comments/', data)
        
        self.assertEqual(response.status_code, 201)
        created_comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(created_comment.author, self.user)

    def test_article_viewset_partial_update(self):
        """Test PATCH /api/articles/{id}/ (ligne 43)"""
        self.client.force_authenticate(user=self.user)
        
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/articles/{self.article.id}/', data)
        
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated Title')

    def test_article_viewset_full_update(self):
        """Test PUT /api/articles/{id}/ (ligne 50)"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Fully Updated Title',
            'content': 'Fully updated content'
        }
        response = self.client.put(f'/api/articles/{self.article.id}/', data)
        
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Fully Updated Title')
