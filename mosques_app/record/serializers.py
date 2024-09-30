from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import serializers

from category.serializers import CategorySerializer

from core.models import Record, Place, Category, Unit
from core.serializers import AuditSerializerMixin
from place.serializers import PlaceSerializer
from user.serializers import UserSerializer



class RecordSerializer(AuditSerializerMixin):
    category = CategorySerializer()
    place = PlaceSerializer()
    created_by = UserSerializer(read_only=True)


    class Meta:
        model = Record
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request', None)
        current_user = request.user
        category_data = validated_data.pop('category', None)
        if category_data is None:
            raise ValidationError('Specify category')

        place_data = validated_data.pop('place', None)

        instance = Record.objects.create(
            category_id=category_data.get('id'),
            place_id=place_data.get('id'),
            created_by=current_user,
            **validated_data
        )

        if current_user.role == 'region_admin' or current_user.role == 'admin':
            place = Place.objects.get(id=place_data.get('id'))

            if place is None:
                raise ValidationError('Specify place id')

            if place.place_type != Place.PlaceType.MOSQUE:
                raise ValidationError('Place type should be MOSQUE')

            if place.parent is None or place.parent.parent is None:
                raise ValidationError('Invalid place is chosen')

            region_parent_id = place.parent.parent.id
            if current_user.role == 'region_admin' and current_user.place is not None and region_parent_id != current_user.place.id:
                raise PermissionDenied('Current mosque does not belong to your region')


        if current_user.role == 'city_admin':
            place_id = instance.place.id
            place = Place.objects.get(pk = place_id)

            if place is None:
                raise ValidationError('Specify place id')

            if place.place_type != Place.PlaceType.MOSQUE:
                raise ValidationError('Place type should be MOSQUE')
            city_parent_id = place.parent.id

            if city_parent_id != current_user.place.id:
                raise PermissionDenied('Current mosque does not belong to your city')

        if current_user.role == 'mosque_admin':
            instance.place = request.user.place

        instance.save(request=request)

        return instance