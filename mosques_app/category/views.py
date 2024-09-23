from rest_framework import viewsets, permissions

from .serializers import CategorySerializer
from core.models import Category

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()

    def get_serializer_context(self):
        # Ensure the request is passed in the context to the serializer
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        # You can call the delete method from the serializer manually if needed
        serializer = self.get_serializer(instance)
        serializer.delete(instance)