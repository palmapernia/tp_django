from django import forms
from .models import Question, Choice

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'is_active']
        widgets = {
            'question_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre question de sondage...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
        widgets = {
            'choice_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option de réponse...'
            })
        }

# Formset pour gérer plusieurs choix
ChoiceFormSet = forms.modelformset_factory(
    Choice, 
    form=ChoiceForm, 
    extra=3, 
    can_delete=True
)