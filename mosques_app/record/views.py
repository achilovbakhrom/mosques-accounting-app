from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Record
from record.serializers import RecordSerializer


class RecordView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Record.objects.all()

    def get_serializer_context(self):
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.delete(instance)
