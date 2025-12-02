from django.contrib import admin
from .models import Choice, Question

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    classes = ['collapse']

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
        ("Author information", {"fields": ["author"]}),
        ("Status", {"fields": ["is_active"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "author", "is_active", "was_published_recently"]
    list_filter = ["pub_date", "is_active", "author"]
    search_fields = ["question_text"]
    date_hierarchy = "pub_date"

admin.site.register(Question, QuestionAdmin)