from rest_framework import viewsets, permissions

from place.serializers import PlaceSerializer
from core.models import Place


# Create your views here.
class PlaceView(viewsets.ModelViewSet):
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Place.objects.all()

    def get_serializer_context(self):
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.delete(instance)