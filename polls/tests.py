from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from polls.models import Question, Choice
import datetime


class QuestionModelTest(TestCase):
    """Tests básicos para el modelo Question"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_question_creation(self):
        """Test de creación de pregunta"""
        question = Question.objects.create(
            question_text='¿Cuál es tu color favorito?',
            author=self.user,
            is_active=True,
        )
        
        self.assertEqual(question.question_text, '¿Cuál es tu color favorito?')
        self.assertEqual(question.author, self.user)
        self.assertTrue(question.is_active)
        self.assertIsNotNone(question.pub_date)
    
    def test_question_string_representation(self):
        """Test de la representación en string de la pregunta"""
        question = Question.objects.create(
            question_text='Test Question',
            author=self.user
        )
        
        self.assertEqual(str(question), 'Test Question')
    
    def test_question_was_published_recently(self):
        """Test del método was_published_recently"""
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertTrue(recent_question.was_published_recently())
        
        # Test con pregunta antigua
        old_time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=old_time)
        self.assertFalse(old_question.was_published_recently())
        
        # Test caso edge: exactamente 24 horas
        edge_time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        edge_question = Question(pub_date=edge_time)
        self.assertFalse(edge_question.was_published_recently())

    def test_can_vote_active_question(self):
        """Test can_vote pour question active"""
        question = Question.objects.create(
            question_text='Active question',
            author=self.user,
            is_active=True
        )
        self.assertTrue(question.can_vote())

    def test_can_vote_inactive_question(self):
        """Test can_vote pour question inactive"""
        question = Question.objects.create(
            question_text='Inactive question',
            author=self.user,
            is_active=False
        )
        self.assertFalse(question.can_vote())


class ChoiceModelTest(TestCase):
    """Tests básicos para el modelo Choice"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.question = Question.objects.create(
            question_text='Test Question',
            author=self.user
        )
    
    def test_choice_creation(self):
        """Test de creación de opción"""
        choice = Choice.objects.create(
            question=self.question,
            choice_text='Opción de prueba',
            votes=0
        )
        
        self.assertEqual(choice.question, self.question)
        self.assertEqual(choice.choice_text, 'Opción de prueba')
        self.assertEqual(choice.votes, 0)
    
    def test_choice_string_representation(self):
        """Test de la representación en string de la opción"""
        choice = Choice.objects.create(
            question=self.question,
            choice_text='Test Choice',
            votes=5
        )
        
        self.assertEqual(str(choice), 'Test Choice')


class PollsViewsTest(TestCase):
    """Tests básicos para las vistas de polls"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.question = Question.objects.create(
            question_text='Test Question',
            author=self.user,
            is_active=True
        )
        self.choice1 = Choice.objects.create(
            question=self.question,
            choice_text='Choice 1',
            votes=0
        )
        self.choice2 = Choice.objects.create(
            question=self.question,
            choice_text='Choice 2',
            votes=0
        )
    
    def test_index_view(self):
        """Test de la vista índice"""
        response = self.client.get(reverse('polls:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Question')
    
    def test_detail_view(self):
        """Test de la vista detalle"""
        response = self.client.get(reverse('polls:detail', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.question_text)
        self.assertContains(response, 'Choice 1')
        self.assertContains(response, 'Choice 2')
    
    def test_results_view(self):
        """Test de la vista de resultados"""
        response = self.client.get(reverse('polls:results', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.question_text)
    
    def test_vote_view(self):
        """Test de votación"""
        data = {'choice': self.choice1.id}
        response = self.client.post(reverse('polls:vote', args=[self.question.id]), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el voto fue registrado
        updated_choice = Choice.objects.get(id=self.choice1.id)
        self.assertEqual(updated_choice.votes, 1)
    
    def test_create_poll_authenticated(self):
        """Test de crear sondage autenticado"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('polls:create_poll'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Créer un nouveau sondage')
    
    def test_create_poll_anonymous(self):
        """Test de crear sondage anónimo"""
        response = self.client.get(reverse('polls:create_poll'))
        
        self.assertEqual(response.status_code, 302)  # Redirige a login
    
    def test_create_poll_post_valid(self):
        """Test de creación de sondage con POST válido"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'question_text': 'New Poll Question',
            'is_active': True,
            'choice_text': ['Option 1', 'Option 2', 'Option 3']
        }
        response = self.client.post(reverse('polls:create_poll'), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la pregunta fue creada
        self.assertTrue(Question.objects.filter(question_text='New Poll Question').exists())
        new_question = Question.objects.get(question_text='New Poll Question')
        self.assertEqual(new_question.author, self.user)
        
        # Verificar que las opciones fueron creadas
        choices = new_question.choice_set.all()
        self.assertEqual(choices.count(), 3)
    
    def test_edit_poll_owner(self):
        """Test de edición de sondage por el propietario"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'question_text': 'Updated Question',
            'is_active': False,
            'choice_text': ['Updated Choice 1', 'Updated Choice 2']
        }
        response = self.client.post(reverse('polls:edit_poll', args=[self.question.id]), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la pregunta fue actualizada
        updated_question = Question.objects.get(id=self.question.id)
        self.assertEqual(updated_question.question_text, 'Updated Question')
        self.assertFalse(updated_question.is_active)
    
    def test_edit_poll_non_owner(self):
        """Test de edición de sondage por no propietario"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.post(reverse('polls:edit_poll', args=[self.question.id]), {
            'question_text': 'Hacked Question'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirige a index
        
        # Verificar que la pregunta NO fue modificada
        unchanged_question = Question.objects.get(id=self.question.id)
        self.assertEqual(unchanged_question.question_text, 'Test Question')
    
    def test_toggle_poll_owner(self):
        """Test de cambio de estado por propietario"""
        self.client.login(username='testuser', password='testpass123')
        
        original_status = self.question.is_active
        response = self.client.post(reverse('polls:toggle_poll', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el estado cambió
        updated_question = Question.objects.get(id=self.question.id)
        self.assertNotEqual(updated_question.is_active, original_status)
    
    def test_toggle_poll_non_owner(self):
        """Test de cambio de estado por no propietario"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        original_status = self.question.is_active
        response = self.client.post(reverse('polls:toggle_poll', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el estado NO cambió
        unchanged_question = Question.objects.get(id=self.question.id)
        self.assertEqual(unchanged_question.is_active, original_status)
    
    def test_delete_poll_get_owner(self):
        """Test de página de confirmación de eliminación para propietario"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('polls:delete_poll', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Supprimer définitivement')
    
    def test_delete_poll_post_owner(self):
        """Test de eliminación por propietario"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('polls:delete_poll', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la pregunta fue eliminada
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())
    
    def test_delete_poll_non_owner(self):
        """Test de eliminación por no propietario"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.post(reverse('polls:delete_poll', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 302)  # Redirige a index
        
        # Verificar que la pregunta NO fue eliminada
        self.assertTrue(Question.objects.filter(id=self.question.id).exists())
    
    def test_vote_inactive_poll(self):
        """Test de votación en sondage desactivado"""
        # Desactivar el sondage
        self.question.is_active = False
        self.question.save()
        
        data = {'choice': self.choice1.id}
        response = self.client.post(reverse('polls:vote', args=[self.question.id]), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ce sondage est fermé')
        
        # Verificar que no se registró el voto
        updated_choice = Choice.objects.get(id=self.choice1.id)
        self.assertEqual(updated_choice.votes, 0)
    
    def test_vote_invalid_choice(self):
        """Test de votación con opción inexistente"""
        data = {'choice': 9999}
        response = self.client.post(reverse('polls:vote', args=[self.question.id]), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You didn&#x27;t select a choice.')
    
    def test_vote_no_choice_selected(self):
        """Test de votación sin seleccionar opción"""
        data = {}
        response = self.client.post(reverse('polls:vote', args=[self.question.id]), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You didn&#x27;t select a choice.')

    def test_edit_poll_get_form(self):
        """Test pour afficher le formulaire d'édition (lignes 128-130)"""
        # Se connecter en tant qu'auteur
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('polls:edit_poll', args=[self.question.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'poll-form')
        self.assertContains(response, self.question.question_text)


class PollsIntegrationTest(TestCase):
    """Test de integración básico"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='polluser',
            email='poll@example.com',
            password='pollpass123'
        )
    
    def test_basic_polls_workflow(self):
        """Test del flujo básico: crear -> votar -> ver resultados"""
        # Login
        self.client.login(username='polluser', password='pollpass123')
        
        # Crear pregunta manualmente para simplificar
        question = Question.objects.create(
            question_text='Test Integration Poll',
            author=self.user,
            is_active=True
        )
        choice = Choice.objects.create(
            question=question,
            choice_text='Test Choice',
            votes=0
        )
        
        # Ver detalle
        response = self.client.get(reverse('polls:detail', args=[question.id]))
        self.assertEqual(response.status_code, 200)
        
        # Votar
        vote_data = {'choice': choice.id}
        response = self.client.post(reverse('polls:vote', args=[question.id]), vote_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar voto
        updated_choice = Choice.objects.get(id=choice.id)
        self.assertEqual(updated_choice.votes, 1)
        
        # Ver resultados
        response = self.client.get(reverse('polls:results', args=[question.id]))
        self.assertEqual(response.status_code, 200)


class PollsAPITestCase(TestCase):
    """Tests pour l'API polls"""
    
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
        
        self.question = Question.objects.create(
            question_text='Test question?',
            author=self.user,
            is_active=True
        )
        
        self.choice1 = Choice.objects.create(
            question=self.question,
            choice_text='Choice 1',
            votes=0
        )
        
        self.choice2 = Choice.objects.create(
            question=self.question,
            choice_text='Choice 2',
            votes=5
        )
        
        self.client = APIClient()

    def test_is_author_or_readonly_permission_safe_methods(self):
        """Test permission pour méthodes sûres (GET, HEAD, OPTIONS)"""
        from polls.views_api import IsAuthorOrReadOnly
        from rest_framework import permissions
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'GET'  # Méthode sûre
        request.user = self.other_user
        
        # Doit permettre l'accès même si pas l'auteur
        self.assertTrue(permission.has_object_permission(request, None, self.question))

    def test_is_author_or_readonly_permission_author(self):
        """Test permission pour l'auteur avec méthodes dangereuses"""
        from polls.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'POST'  # Méthode dangereuse
        request.user = self.user
        
        # Doit permettre l'accès car c'est l'auteur
        self.assertTrue(permission.has_object_permission(request, None, self.question))

    def test_is_author_or_readonly_permission_not_author(self):
        """Test permission pour non-auteur avec méthodes dangereuses"""
        from polls.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'POST'  # Méthode dangereuse
        request.user = self.other_user
        
        # Ne doit pas permettre l'accès car pas l'auteur
        self.assertFalse(permission.has_object_permission(request, None, self.question))

    def test_is_author_or_readonly_permission_no_author_attr(self):
        """Test permission avec objet sans attribut author ou question (ligne 18)"""
        from polls.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'DELETE'
        request.user = self.user
        
        # Objet mock sans attribut author ni question
        fake_obj = Mock(spec=[])
        
        # Doit retourner False car pas d'attribut author
        self.assertFalse(permission.has_object_permission(request, None, fake_obj))

    def test_is_author_or_readonly_permission_choice_object(self):
        """Test permission pour objets Choice"""
        from polls.views_api import IsAuthorOrReadOnly
        from unittest.mock import Mock
        
        permission = IsAuthorOrReadOnly()
        request = Mock()
        request.method = 'DELETE'  # Méthode dangereuse
        request.user = self.user
        
        # Doit permettre l'accès car l'utilisateur est l'auteur de la question
        self.assertTrue(permission.has_object_permission(request, None, self.choice1))

    def test_question_viewset_list(self):
        """Test GET /polls/api/questions/"""
        response = self.client.get('/polls/api/questions/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question_text'], 'Test question?')

    def test_question_viewset_create_authenticated(self):
        """Test POST /polls/api/questions/ avec authentification"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'question_text': 'New question?',
            'is_active': True
        }
        
        response = self.client.post('/polls/api/questions/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['question_text'], 'New question?')
        self.assertEqual(response.data['author'], self.user.id)

    def test_question_viewset_create_unauthenticated(self):
        """Test POST /polls/api/questions/ sans authentification"""
        data = {
            'question_text': 'New question?',
            'is_active': True
        }
        
        response = self.client.post('/polls/api/questions/', data)
        
        self.assertEqual(response.status_code, 401)

    def test_question_vote_action(self):
        """Test POST /polls/api/questions/{id}/vote/"""
        self.client.force_authenticate(user=self.user)
        
        data = {'choice_id': self.choice1.id}
        response = self.client.post(f'/polls/api/questions/{self.question.id}/vote/', data)
        
        self.assertEqual(response.status_code, 200)
        self.choice1.refresh_from_db()
        self.assertEqual(self.choice1.votes, 1)

    def test_question_vote_inactive_poll(self):
        """Test vote sur sondage fermé"""
        self.question.is_active = False
        self.question.save()
        
        self.client.force_authenticate(user=self.user)
        
        data = {'choice_id': self.choice1.id}
        response = self.client.post(f'/polls/api/questions/{self.question.id}/vote/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('fermé', response.data['error'])

    def test_question_vote_missing_choice_id(self):
        """Test vote sans choice_id"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(f'/polls/api/questions/{self.question.id}/vote/', {})
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('requis', response.data['error'])

    def test_question_vote_invalid_choice(self):
        """Test vote avec choix invalide"""
        self.client.force_authenticate(user=self.user)
        
        data = {'choice_id': 99999}  # ID inexistant
        response = self.client.post(f'/polls/api/questions/{self.question.id}/vote/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('n\'existe pas', response.data['error'])

    def test_question_vote_unauthenticated(self):
        """Test vote sans authentification"""
        data = {'choice_id': self.choice1.id}
        response = self.client.post(f'/polls/api/questions/{self.question.id}/vote/', data)
        
        self.assertEqual(response.status_code, 401)

    def test_question_results_action(self):
        """Test GET /polls/api/questions/{id}/results/"""
        response = self.client.get(f'/polls/api/questions/{self.question.id}/results/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_question_toggle_status_action_author(self):
        """Test POST /polls/api/questions/{id}/toggle_status/ par l'auteur"""
        self.client.force_authenticate(user=self.user)
        
        original_status = self.question.is_active
        response = self.client.post(f'/polls/api/questions/{self.question.id}/toggle_status/')
        
        self.assertEqual(response.status_code, 200)
        self.question.refresh_from_db()
        self.assertEqual(self.question.is_active, not original_status)

    def test_question_toggle_status_action_not_author(self):
        """Test POST /polls/api/questions/{id}/toggle_status/ par non-auteur"""
        self.client.force_authenticate(user=self.other_user)
        
        response = self.client.post(f'/polls/api/questions/{self.question.id}/toggle_status/')
        
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_choice_viewset_list(self):
        """Test GET /polls/api/choices/"""
        response = self.client.get('/polls/api/choices/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_choice_viewset_filter_by_question(self):
        """Test GET /polls/api/choices/?question={id}"""
        response = self.client.get(f'/polls/api/choices/?question={self.question.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_choice_viewset_create_authenticated(self):
        """Test POST /polls/api/choices/ avec authentification"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'question': self.question.id,
            'choice_text': 'New choice'
        }
        
        response = self.client.post('/polls/api/choices/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['choice_text'], 'New choice')
