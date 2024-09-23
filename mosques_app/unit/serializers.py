from core.models import Unit
from core.serializers import AuditSerializerMixin


class UnitSerializer(AuditSerializerMixin):
    """Unit serializer"""
    class Meta:
        model = Unit
        fields = ['id', 'name']
        read_only_fields = ['id']

    # def create(self, validated_data):
    #     request = self.context.get('request', None)
    #
    #     # Create a new Unit instance
    #
    #     instance = self.Meta.model(**validated_data)
    #
    #     # Call save() on the instance and pass the request
    #     instance.save(request=request)
    #
    #     return instance
    #
    # def update(self, instance, validated_data):
    #     request = self.context.get('request', None)
    #
    #     # Update the instance with the validated data
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #
    #     # Call save() on the instance and pass the request
    #     instance.save(request=request)
    #
    #     return instance
    #
    # def delete(self, instance):
    #     request = self.context.get('request', None)
    #
    #     instance.delete(request=request)

