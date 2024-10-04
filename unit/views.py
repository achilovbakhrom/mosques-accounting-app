from rest_framework import viewsets, permissions

from unit.serializers import UnitSerializer
from core.models import Unit
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

class UnitView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Unit.objects.all()

    def get_serializer_context(self):
        # Ensure the request is passed in the context to the serializer
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        # You can call the delete method from the serializer manually if needed
        serializer = self.get_serializer(instance)
        serializer.delete(instance)

