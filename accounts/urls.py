from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
 TokenObtainPairView,
 TokenRefreshView,
)
from .views import RegisterView, ProfileUpdateView

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    # API URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/profile/', ProfileUpdateView.as_view(), name='profile_api'),
]