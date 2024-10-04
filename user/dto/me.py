from rest_framework import  serializers
from django.contrib.auth import get_user_model

from place.serializers import PlaceSerializer


class MeSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'name', 'role', 'place']