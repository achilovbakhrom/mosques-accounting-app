from core.models import Category
from core.serializers import AuditSerializerMixin


class CategorySerializer(AuditSerializerMixin):
    """Category serializer"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'operation_type', 'unit']
        read_only_fields = ['id']
