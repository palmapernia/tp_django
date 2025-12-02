from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_api import QuestionViewSet, ChoiceViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)

app_name = "polls"
urlpatterns = [
 
 # ex: /polls/
 path("", views.IndexView.as_view(), name="index"),
 # ex: /polls/5/
 path("<int:pk>/", views.DetailView.as_view(), name="detail"),
 # ex: /polls/5/results/
 path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
 # ex: /polls/5/vote/
 path("<int:question_id>/vote/", views.vote, name="vote"),
 
 # CRUD operations
 path("create/", views.create_poll, name="create_poll"),
 path("<int:question_id>/edit/", views.edit_poll, name="edit_poll"),
 path("<int:question_id>/toggle/", views.toggle_poll_status, name="toggle_poll"),
 path("<int:question_id>/delete/", views.delete_poll, name="delete_poll"),
 # API URLs
 path('api/', include(router.urls)),
]