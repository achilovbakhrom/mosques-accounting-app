from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.models import Record, Place
from core.pagination import CustomPagination
from record.serializers import RecordSerializer


class RecordView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = RecordSerializer
    pagination_class = CustomPagination
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
    def list(self, request, *args, **kwargs):
        qp_place_id = request.query_params.get('place_id')
        user = request.user

        if qp_place_id is None and user.role != 'mosque_admin':
            raise ValidationError('Specify place id for not mosque admins')

        place_id = qp_place_id or user.place.id
        found = Place.objects.get(pk=place_id)

        if found is None:
            raise ValidationError('Provide a valid place id')

        ids = []

        ids.append(found.id)
        if found.parent is not None:
            ids.append(found.parent.id)
            if found.parent.parent is not None:
                ids.append(found.parent.parent.id)


        if user.place.id not in ids:
            raise ValidationError('Place id does not belong to your area')

        records = Record.objects.filter(place_id=place_id)

        paginator = self.pagination_class()

        try:
            # Paginate the queryset
            page = paginator.paginate_queryset(records, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        except NotFound:
            # Handle the invalid page case, return an empty result set
            return Response(
                {
                    "count": records.count(),
                    "next": None,
                    "previous": None,
                    "results": []
                },
                status=200
            )

        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


    def get_serializer_context(self):
        context = super(type(self), self).get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.delete(instance)