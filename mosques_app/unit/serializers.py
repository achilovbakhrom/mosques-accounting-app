from core.models import Unit
from core.serializers import AuditSerializerMixin


class UnitSerializer(AuditSerializerMixin):
    """Unit serializer"""
    class Meta:
        model = Unit
        fields = '__all__'

