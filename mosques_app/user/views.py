""" Views for the user API. """
from rest_framework import generics, permissions

from core.models import ActivityLog
from core.utils import get_client_ip
from user.serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


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