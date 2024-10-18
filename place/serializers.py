from core.models import Place
from core.serializers import AuditSerializerMixin


class PlaceSerializer(AuditSerializerMixin):
    class Meta:
        model = Place
        fields = ['id', 'name', 'inn', 'is_mosque', 'parent']
        read_only = ['id']


