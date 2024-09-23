from core.models import Place
from core.serializers import AuditSerializerMixin


class PlaceSerializer(AuditSerializerMixin):
    class Meta:
        model = Place
        fields = ['id', 'name', 'parent', 'place_type']
        read_only = ['id']