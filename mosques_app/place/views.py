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
    def _get_place_type(place_id):
        place = Place.objects.get(pk = place_id)

        return place.place_type

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
        places = None
        match role:
            case 'admin':
                if place_id is None:
                    places = query_set.filter(place_type=Place.PlaceType.REGION)
                else:
                    places = query_set.filter(parent = place_id)
            case 'region_admin':
                if qp_place_id is None:
                    place_id = current_user.place_id
                    places = query_set.filter(parent = place_id)
                elif qp_place_id is not None:
                    place_type = self._get_place_type(qp_place_id)
                    if place_type == Place.PlaceType.REGION and qp_place_id != str(current_user.place_id):
                        raise PermissionDenied('User does not have permission')
                    elif place_type == Place.PlaceType.REGION and qp_place_id == str(current_user.place_id):
                        places = query_set.filter(parent=qp_place_id)
                    elif place_type == Place.PlaceType.CITY:
                        parent = self._get_city_parent_id(qp_place_id)
                        if parent == current_user.place_id:
                            places = query_set.filter(parent=qp_place_id)
                        else:
                            raise PermissionDenied('User does not have permission')
                    elif place_type == Place.PlaceType.MOSQUE:
                        raise NotFound('Endpoint does not support mosque type')
                    else:
                        places = []
            case 'city_admin':
                place_type = self._get_place_type(place_id)
                if qp_place_id is None or qp_place_id == str(current_user.place_id):
                    places = query_set.filter(parent=current_user.place_id)
                elif place_type == Place.PlaceType.REGION:
                    raise PermissionDenied('User does not have permission')
                elif place_type == Place.PlaceType.MOSQUE:
                    raise NotFound('Endpoint does not support mosque type')
                elif qp_place_id is not None and place_type == Place.PlaceType.CITY and qp_place_id != str(current_user.place_id):
                    raise PermissionDenied('User does not have permission')
                else:
                    places = []
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