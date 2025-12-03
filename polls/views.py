from django.shortcuts import get_object_or_404, render, redirect
from django.http import  HttpResponseRedirect
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from .models import Choice, Question
from .forms import QuestionForm, ChoiceFormSet
from django.views import generic
from django.contrib.auth.decorators import login_required

# Create your views here.

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        # Calcular el total de votos
        total_votes = sum(choice.votes for choice in question.choice_set.all())
        context['total_votes'] = total_votes if total_votes > 0 else 1  # Evitar división por 0
        return context

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # Verificar si el sondage está activo
    if not question.is_active:
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Ce sondage est fermé et n'accepte plus de votes.",
            },
        )
    
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing with POST data.
        # This prevents data from being posted twice if a user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


@login_required
def create_poll(request):
    """Créer un nouveau sondage"""
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.author = request.user
            question.pub_date = timezone.now()
            question.save()
            
            # Traiter les choix
            choice_texts = request.POST.getlist('choice_text')
            for choice_text in choice_texts:
                if choice_text.strip():  # Ignorer les choix vides
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text.strip()
                    )
            
            return redirect('polls:index')
    else:
        question_form = QuestionForm()
    
    return render(request, 'polls/create_poll.html', {
        'question_form': question_form
    })


@login_required
def edit_poll(request, question_id):
    """Modifier un sondage existant"""
    question = get_object_or_404(Question, pk=question_id)
    
    # Vérifier que l'utilisateur est l'auteur
    if question.author != request.user:
        return redirect('polls:index')
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        
        if question_form.is_valid():
            question_form.save()
            
            # Supprimer tous les anciens choix et créer les nouveaux
            question.choice_set.all().delete()
            choice_texts = request.POST.getlist('choice_text')
            for choice_text in choice_texts:
                if choice_text.strip():
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text.strip()
                    )
            
            # Detectar desde dónde viene y mantener el parámetro 'from'
            from_param = request.GET.get('from')
            referer = request.META.get('HTTP_REFERER', '')
            
            if 'results' in referer:
                # Viene desde results, regresar a results
                if from_param:
                    return redirect(f"{reverse('polls:results', args=[question.id])}?from={from_param}")
                else:
                    return redirect('polls:results', question.id)
            else:
                # Viene desde detail, regresar a detail
                if from_param:
                    return redirect(f"{reverse('polls:detail', args=[question.id])}?from={from_param}")
                else:
                    return redirect('polls:detail', question.id)
    else:
        question_form = QuestionForm(instance=question)
    
    return render(request, 'polls/edit_poll.html', {
        'question': question,
        'question_form': question_form,
        'choices': question.choice_set.all()
    })


@login_required
def toggle_poll_status(request, question_id):
    """Activer/désactiver un sondage"""
    question = get_object_or_404(Question, pk=question_id)
    
    if question.author == request.user:
        question.is_active = not question.is_active
        question.save()
        
        # Detectar desde dónde viene y mantener el parámetro 'from'
        from_param = request.GET.get('from')
        referer = request.META.get('HTTP_REFERER', '')
        
        if 'results' in referer:
            # Viene desde results, regresar a results
            if from_param:
                return redirect(f"{reverse('polls:results', args=[question.id])}?from={from_param}")
            else:
                return redirect('polls:results', question.id)
        else:
            # Viene desde detail, regresar a detail
            if from_param:
                return redirect(f"{reverse('polls:detail', args=[question.id])}?from={from_param}")
            else:
                return redirect('polls:detail', question.id)
    
    return redirect('polls:detail', question.id)


@login_required
def delete_poll(request, question_id):
    """Supprimer un sondage"""
    question = get_object_or_404(Question, pk=question_id)
    
    if question.author == request.user:
        if request.method == 'POST':
            question.delete()
            return redirect('polls:index')
        return render(request, 'polls/confirm_delete.html', {'question': question})
    
    return redirect('polls:index')
