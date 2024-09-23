from core.serializers import AuditSerializerMixin

from core.models import Record


class RecordSerializer(AuditSerializerMixin):
    class Meta:
        model = Record
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request', None)

        # Create a new Unit instance

        instance = self.Meta.model(**validated_data)

        instance.place = request.user.place

        # Call save() on the instance and pass the request
        instance.save(request=request)

        return instance