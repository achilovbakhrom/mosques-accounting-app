from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, filters
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.pagination import CustomPagination
from core.permissions.IsNotMosqueAdmin import IsNotMosqueAdmin
from place.serializers import PlaceSerializer
from core.models import Place

class PlaceDetailView(generics.RetrieveAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class PlaceViewMosques(generics.ListAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    queryset = Place.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='place_id', description='PlaceId', required=False, type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally filter the queryset by a custom query parameter (e.g., 'published_year')
        in addition to the search functionality provided by SearchFilter.
        """
        queryset = super().get_queryset()

        # Get the 'published_year' query parameter
        parent_id = self.request.query_params.get('place_id', None)

        if parent_id:
            # Filter by the year of publication
            queryset = queryset.filter(parent=parent_id)

        return queryset

# Create your views here.
class PlaceView(generics.ListAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsNotMosqueAdmin]
    pagination_class = CustomPagination
    queryset = Place.objects.all()

    @staticmethod
    def _place_id_belongs_to(place_id: int, user_place_id: int):
        if place_id == user_place_id:
            return True

        found_place = Place.objects.get(pk = place_id)
        if found_place is not None:
            parent = found_place.parent
            while parent is not None:
                if parent.id == user_place_id:
                    return True

        return False

    @staticmethod
    def _get_city_parent_id(place_id):
        place = Place.objects.get(pk=place_id)
        if place is not None and place.parent is not None:
            return place.parent.id
        else:
            return None

    @extend_schema(
        parameters=[
            OpenApiParameter(name='place_id', description='PlaceId', required=False, type=int),
        ]
    )
    def get(self, request):
        query_set = self.get_queryset()
        current_user = request.user
        qp_place_id = request.query_params.get('place_id')
        place_id = qp_place_id or current_user.place_id
        role = current_user.role

        match role:
            case 'admin':
                places = query_set.filter(parent = place_id)
            case 'region_admin':
                if self._place_id_belongs_to(int(place_id), int(current_user.place_id)):
                    places = query_set.filter(parent = place_id)
                else:
                    raise PermissionDenied('User does not have permission')
            case 'mosque_admin':
                raise NotFound('Endpoint does not support mosque type')
            case _:
                places = []

        paginator = self.pagination_class()
        try:
            # Paginate the queryset
            page = paginator.paginate_queryset(places, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        except NotFound:
            # Handle the invalid page case, return an empty result set
            return Response(
                {
                    "count": places.count(),
                    "next": None,
                    "previous": None,
                    "results": []
                },
                status=200
            )

        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)