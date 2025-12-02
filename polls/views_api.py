from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question, Choice
from .serializers import QuestionSerializer, ChoiceSerializer

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Pour Question, vérifier l'auteur directement
        if hasattr(obj, 'author'):
            return obj.author == request.user
        # Pour Choice, vérifier l'auteur de la question associée
        elif hasattr(obj, 'question') and hasattr(obj.question, 'author'):
            return obj.question.author == request.user
        return False

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def get_queryset(self):
        # Filtrer par question si spécifié
        question_id = self.request.query_params.get('question')
        if question_id:
            return Choice.objects.filter(question_id=question_id)
        return Choice.objects.all()

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('-pub_date')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        summary="Voter pour un choix",
        description="Permet de voter pour un choix spécifique dans ce sondage"
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        """Action personnalisée pour voter"""
        question = self.get_object()
        
        # Vérifier que le sondage est actif
        if not question.is_active:
            return Response(
                {'error': 'Ce sondage est fermé et n\'accepte plus de votes.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer le choix
        choice_id = request.data.get('choice_id')
        if not choice_id:
            return Response(
                {'error': 'choice_id est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            choice = question.choice_set.get(id=choice_id)
        except Choice.DoesNotExist:
            return Response(
                {'error': 'Ce choix n\'existe pas pour ce sondage.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Voter (incrementer)
        from django.db.models import F
        choice.votes = F('votes') + 1
        choice.save()
        
        # Recharger pour avoir la valeur actuelle
        choice.refresh_from_db()
        
        return Response({
            'message': 'Vote enregistré avec succès.',
            'choice': ChoiceSerializer(choice).data
        })

    @extend_schema(
        summary="Obtenir les résultats du sondage",
        description="Retourne les résultats détaillés avec statistiques"
    )
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Action pour voir les résultats"""
        question = self.get_object()
        choices = question.choice_set.all()
        total_votes = sum(choice.votes for choice in choices)
        
        results_data = {
            'question': QuestionSerializer(question).data,
            'total_votes': total_votes,
            'results': []
        }
        
        for choice in choices:
            percentage = (choice.votes / total_votes * 100) if total_votes > 0 else 0
            results_data['results'].append({
                'choice': ChoiceSerializer(choice).data,
                'percentage': round(percentage, 2)
            })
        
        return Response(results_data)

    @extend_schema(
        summary="Basculer le statut actif/inactif",
        description="Active ou désactive le sondage (réservé à l'auteur)"
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_status(self, request, pk=None):
        """Action pour activer/désactiver le sondage"""
        question = self.get_object()
        
        # Vérifier que l'utilisateur est l'auteur
        if question.author != request.user:
            return Response(
                {'error': 'Seul l\'auteur peut modifier le statut.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        question.is_active = not question.is_active
        question.save()
        
        return Response({
            'message': f'Sondage {"activé" if question.is_active else "désactivé"} avec succès.',
            'is_active': question.is_active
        })