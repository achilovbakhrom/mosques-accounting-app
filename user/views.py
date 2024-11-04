""" Views for the user API. """
import json

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView


from core.models import ActivityLog
from core.utils import get_client_ip
from user.serializers import UserSerializer, CustomTokenObtainPairSerializer
from .dto.me import MeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer

class ManageUserView(generics.RetrieveAPIView):
    """Manage the authenticated user."""
    serializer_class = MeSerializer
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        user = self.request.user

        return user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            # Get the refresh token
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)

            # Blacklist the token (this invalidates the token)
            token.blacklist()

            # Log the logout activity
            remote_addr = get_client_ip(request)
            ActivityLog.objects.create(
                user=request.user,  # Pass request from view
                action='logout',
                object_id=None,
                object_type=None,
                description=f'{request.user.username} logged out with from {remote_addr}',
                ip_address=remote_addr
            )

            return Response({"detail": "Logout successful."}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class UserPlaceView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        queryset = self.queryset.all()
        place_id = self.kwargs.get('place_id')

        if place_id is None:
            raise ValueError('Place id is required')

        return queryset.filter(place_id=place_id)
