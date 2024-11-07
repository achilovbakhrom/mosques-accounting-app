from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from category.serializers import CategorySerializer

from core.models import Record, Place
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

        place = Place.objects.get(id=place_data.get('id'))

        if current_user.role == 'region_admin' or current_user.role == 'admin':

            if place is None:
                raise ValidationError('Specify place id')

            if not place.is_mosque:
                raise ValidationError('Place type should be MOSQUE')


        if current_user.role == 'mosque_admin':
            instance.place = request.user.place

        instance.save(request=request)

        return instance

class ReportValueSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField(source='category__name')
    unit_name = serializers.CharField(source='category__unit__name')
    total_quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Renaming fields
        data['category_id'] = instance['category_id']
        data['category_name'] = instance['category__name']
        data['unit_name'] = instance['category__unit__name']
        data['total_quantity'] = instance['total_quantity']
        return data