"""
URL mappings for the user API.
"""
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from user import views

app_name = 'user'

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('logout/', views.LogoutView.as_view(), name='remove_token'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('place/<int:place_id>/', views.UserPlaceView.as_view(), name='user_by_place_id')
]
