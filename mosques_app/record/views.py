from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.models import Record
from record.serializers import RecordSerializer


class RecordView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Record.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='from', description='Date From YYYY-MM-DD', required=False, type=str),
            OpenApiParameter(name='to', description='Date To YYYY-MM-DD', required=False, type=str),
            OpenApiParameter(name='place_id', description='PlaceId', required=False, type=int),
        ],
        responses={200: RecordSerializer}
    )
    @action(detail=False, methods=['get'])
    def get_data(self, request: Request):
        user = request.user
        place_id = request.query_params.get('place_id')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        

        return Response({ 'status': 123 })

    def get_serializer_context(self):
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.delete(instance)
