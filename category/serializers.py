from core.models import Category
from core.serializers import AuditSerializerMixin
from unit.serializers import UnitSerializer


class CategorySerializer(AuditSerializerMixin):
    unit = UnitSerializer(required=False, allow_null=True)
    """Category serializer"""
    class Meta:
        model = Category
        fields = '__all__'

