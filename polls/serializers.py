from rest_framework import serializers
from .models import Question, Choice
from django.contrib.auth.models import User

class ChoiceSerializer(serializers.ModelSerializer):
    question_author_username = serializers.ReadOnlyField(source='question.author.username')
    
    class Meta:
        model = Choice
        fields = ['id', 'question', 'choice_text', 'votes', 'question_author_username']
        read_only_fields = ['votes']

class QuestionSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    choices = ChoiceSerializer(source='choice_set', many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'author', 'author_username', 'is_active', 'choices']
        read_only_fields = ['author', 'pub_date']